"""Custom BaseLLM implementation that routes LLM calls through SAP AICore
instead of LiteLLM, avoiding the dead localhost:6655 proxy.

Uses gen_ai_hub's Bedrock client to call Claude models deployed on AICore.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from gen_ai_hub.proxy.native.amazon.clients import Session

from harbor.llms.base import BaseLLM, LLMResponse, OutputLengthExceededError
from harbor.models.metric import UsageInfo

from aicore_llm_access import ClaudeModels

logger = logging.getLogger(__name__)

# Map common model name patterns to AICore ClaudeModels entries
_MODEL_MAP: dict[str, ClaudeModels] = {}
for m in ClaudeModels:
    _MODEL_MAP[m.alias] = m
    _MODEL_MAP[m.model_name] = m
# Also map some common litellm-style names
_MODEL_MAP.update({
    "claude-opus-4-5-20251101": ClaudeModels.CLAUDE_OPUS,
    "anthropic/claude-opus-4-5-20251101": ClaudeModels.CLAUDE_OPUS,
    "claude-4-sonnet": ClaudeModels.CLAUDE_4,
    "anthropic/claude-4-sonnet": ClaudeModels.CLAUDE_4,
    "claude-sonnet-4-20250514": ClaudeModels.CLAUDE_4,
    "anthropic/claude-sonnet-4-20250514": ClaudeModels.CLAUDE_4,
})


def _resolve_model(model_name: str) -> ClaudeModels:
    """Resolve a model name string to an AICore ClaudeModels enum entry."""
    if model_name in _MODEL_MAP:
        return _MODEL_MAP[model_name]
    # Try case-insensitive / partial match
    lower = model_name.lower()
    for key, val in _MODEL_MAP.items():
        if key.lower() == lower:
            return val
    # Default to Opus
    logger.warning("Unknown model %r, defaulting to claude_opus", model_name)
    return ClaudeModels.CLAUDE_OPUS


class AICoreAnthropicLLM(BaseLLM):
    """LLM backend that calls Claude via SAP AICore's Bedrock-compatible API."""

    def __init__(
        self,
        model_name: str = "claude_opus",
        temperature: float = 0.7,
        max_tokens: int = 16384,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._model_enum = _resolve_model(model_name)
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._logger = logger.getChild(self.__class__.__name__)
        self._logger.info(
            "AICore LLM initialized: %s (deployment=%s)",
            self._model_enum.model_name,
            self._model_enum.deployment_id,
        )

    def _get_bedrock_client(self):
        """Create a fresh Bedrock client (handles token refresh)."""
        session = Session()
        return session.client(
            model_name=self._model_enum.model_name,
            deployment_id=self._model_enum.deployment_id,
        )

    def _format_messages(
        self, prompt: str, message_history: list[dict[str, Any]]
    ) -> tuple[list[dict], list[dict]]:
        """Convert Harbor chat format to Bedrock converse() format.

        Returns:
            (system_messages, conversation_messages) tuple.
        """
        all_messages = list(message_history) + [{"role": "user", "content": prompt}]

        system_messages = []
        conversation_messages = []

        for msg in all_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_messages.append({"text": content})
            else:
                # Bedrock expects content as list of content blocks
                if isinstance(content, str):
                    content_blocks = [{"text": content}]
                elif isinstance(content, list):
                    # Already in block format
                    content_blocks = []
                    for block in content:
                        if isinstance(block, str):
                            content_blocks.append({"text": block})
                        elif isinstance(block, dict) and "text" in block:
                            content_blocks.append({"text": block["text"]})
                        else:
                            content_blocks.append({"text": str(block)})
                else:
                    content_blocks = [{"text": str(content)}]

                conversation_messages.append({
                    "role": role,
                    "content": content_blocks,
                })

        return system_messages, conversation_messages

    def _call_sync(
        self, prompt: str, message_history: list[dict[str, Any]]
    ) -> LLMResponse:
        """Synchronous call to AICore Bedrock client."""
        client = self._get_bedrock_client()
        system_msgs, conv_msgs = self._format_messages(prompt, message_history)

        converse_kwargs: dict[str, Any] = {
            "messages": conv_msgs,
            "inferenceConfig": {
                "maxTokens": self._max_tokens,
                "temperature": self._temperature,
            },
        }
        if system_msgs:
            converse_kwargs["system"] = system_msgs

        response = client.converse(**converse_kwargs)

        # Extract content
        output = response.get("output", {})
        message = output.get("message", {})
        content_blocks = message.get("content", [])
        content = ""
        for block in content_blocks:
            if "text" in block:
                content += block["text"]

        # Extract usage
        usage_data = response.get("usage", {})
        prompt_tokens = usage_data.get("inputTokens", 0)
        completion_tokens = usage_data.get("outputTokens", 0)
        # AICore/Bedrock doesn't report cache tokens the same way
        cache_tokens = 0

        usage = UsageInfo(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cache_tokens=cache_tokens,
            cost_usd=0.0,  # AICore doesn't report cost
        )

        # Check stop reason
        stop_reason = response.get("stopReason", "end_turn")
        if stop_reason == "max_tokens":
            raise OutputLengthExceededError(
                f"Model hit max_tokens limit ({self._max_tokens}). Response truncated.",
                truncated_response=content,
            )

        return LLMResponse(
            content=content,
            reasoning_content=None,
            model_name=self._model_enum.model_name,
            usage=usage,
        )

    async def call(
        self,
        prompt: str,
        message_history: list[dict[str, Any]] | None = None,
        response_format: Any = None,
        logging_path: Any = None,
        **kwargs,
    ) -> LLMResponse:
        """Async call to AICore. Wraps synchronous Bedrock client in a thread."""
        if message_history is None:
            message_history = []

        return await asyncio.to_thread(self._call_sync, prompt, message_history)

    def get_model_context_limit(self) -> int:
        """Claude Opus 4.5 supports 200k context."""
        return 200000

    def get_model_output_limit(self) -> int | None:
        """Claude Opus 4.5 supports up to 32k output tokens."""
        return 32000
