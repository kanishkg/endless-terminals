"""Drop-in replacement for ``generator.chat_completion_batch`` that routes
requests through SAP AICore instead of a local vLLM server.

Usage — swap the import in generate_tasks.py or any generator module:

    from generator.aicore_batch import chat_completion_batch

The returned list is structurally identical to the one produced by the
original ``chat_completion_batch``: each element is either a fake response
object exposing ``resp.choices[0].message.content`` (a string), or ``None``
on failure.  All downstream code (task_template_gen, initial_state_test_gen,
completion_test_gen) works without modification.
"""
from __future__ import annotations

import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from tqdm import tqdm

# Allow running from the repo root or from inside endless-terminals-main
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from aicore_llm_access import get_anthropic_completion, model_aliases

logger = logging.getLogger(__name__)

MAX_RETRIES = 5

# Models recognised by aicore_llm_access; anything else falls back to claude_4
_AICORE_MODELS = set(model_aliases)  # {"claude_3.5", "claude_3.7", "claude_4"}


def _resolve_model(model: str) -> str:
    """Return a valid AICore alias, defaulting to claude_4 for unknown names."""
    if model in _AICORE_MODELS:
        return model
    logger.warning("Model %r is not an AICore alias; falling back to 'claude_4'.", model)
    return "claude_4"


def _make_response(content: str) -> SimpleNamespace:
    """Wrap a plain string in a minimal OpenAI-response-shaped namespace.

    Downstream code accesses: ``resp.choices[0].message.content``
    """
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


def chat_completion_batch(
    messages: List[List[Dict[str, str]]],
    model: str = "claude_4",
    temperature: float = 0.8,
    max_tokens: int = 4000,
    num_completions: int = 1,  # accepted for API compatibility; AICore returns one completion
    max_concurrency: int = 16,
    show_progress: bool = True,
    **_kwargs: Any,
) -> List[Optional[SimpleNamespace]]:
    """Submit multiple chat-completion requests to AICore concurrently.

    Parameters mirror the original ``chat_completion_batch`` signature so that
    all call-sites in the generator modules work without changes.

    Returns a list aligned to ``messages``: each element is either a response
    namespace (``resp.choices[0].message.content`` → str) or ``None``.
    """
    aicore_model = _resolve_model(model)
    results: List[Optional[SimpleNamespace]] = [None] * len(messages)

    def _call_with_retry(idx: int, msgs: List[Dict[str, str]]) -> Optional[SimpleNamespace]:
        # Filter out system messages — AICore/Bedrock converse() expects them
        # as a leading dict with role="system", which get_anthropic_completion
        # already handles transparently via the messages list.
        last_exc: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                text = get_anthropic_completion(
                    messages=msgs,
                    model=aicore_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return _make_response(text)
            except Exception as exc:
                last_exc = exc
                wait = min(2 ** attempt, 30)
                logger.debug("Attempt %d failed for request %d: %s. Retrying in %ds.", attempt + 1, idx, exc, wait)
                time.sleep(wait)
        logger.error("All %d attempts failed for request %d: %s", MAX_RETRIES, idx, last_exc)
        return None

    with ThreadPoolExecutor(max_workers=max_concurrency) as pool:
        future_to_idx = {pool.submit(_call_with_retry, i, m): i for i, m in enumerate(messages)}

        pbar = tqdm(
            total=len(messages),
            disable=not show_progress,
            dynamic_ncols=True,
            desc="AICore requests",
            unit="req",
            file=sys.stdout,
        )
        try:
            for fut in as_completed(future_to_idx):
                idx = future_to_idx[fut]
                try:
                    results[idx] = fut.result()
                except Exception as exc:
                    logger.error("Unexpected error for request %d: %s", idx, exc)
                    results[idx] = None
                finally:
                    pbar.update(1)
        finally:
            pbar.close()

    failed = [i for i, r in enumerate(results) if r is None]
    if failed:
        logger.warning("%d / %d requests failed: indices %s", len(failed), len(messages), failed)

    return results