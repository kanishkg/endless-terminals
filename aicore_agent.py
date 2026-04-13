"""Custom Harbor agent: Terminus-2 with AICore LLM backend.

Subclasses Terminus2 and replaces the LiteLLM backend with AICoreAnthropicLLM
so that LLM calls go through SAP AICore instead of the dead localhost proxy.

Usage with harbor CLI:
    harbor run \
        --path harbor_tasks \
        --agent-import-path aicore_agent:AICoreTerminus2 \
        --model claude_opus \
        --n-attempts 2 \
        --n-concurrent 2 \
        --jobs-dir harbor_jobs_aicore \
        --yes
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from harbor.agents.terminus_2.terminus_2 import Terminus2

from aicore_llm import AICoreAnthropicLLM


class AICoreTerminus2(Terminus2):
    """Terminus-2 agent with AICore as the LLM backend."""

    def __init__(
        self,
        logs_dir: Path,
        model_name: str | None = None,
        temperature: float = 0.7,
        **kwargs,
    ):
        # Terminus2.__init__ requires a model_name that LiteLLM can resolve
        # for get_supported_openai_params(). Use a known Anthropic model name
        # so the parent init doesn't crash, then swap the LLM.
        litellm_model = "anthropic/claude-opus-4-5-20251101"

        # Pop AICore-specific kwargs before passing to parent
        aicore_model = model_name or "claude_opus"

        super().__init__(
            logs_dir=logs_dir,
            model_name=litellm_model,
            temperature=temperature,
            **kwargs,
        )

        # Replace the LiteLLM backend with AICore.
        # Terminus2.run() creates Chat(self._llm, ...) at the start of each run,
        # so swapping self._llm here is sufficient.
        self._llm = AICoreAnthropicLLM(
            model_name=aicore_model,
            temperature=temperature,
        )

    @staticmethod
    def name() -> str:
        return "aicore-terminus-2"

    def version(self) -> str | None:
        return "1.0.0"
