"""Unit tests for AICore LLM access layer.

Tests ClaudeModels enum, model resolution, message formatting, and
the generate_harbor_solutions action parser. All AICore network calls
are mocked so these tests run offline.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.aicore_llm_access import ClaudeModels, get_anthropic_completion, model_aliases
from generator.sample_solutions import _extract_action
from generator.collect_harbor_results import compute_pass_at_k


# ---------------------------------------------------------------------------
# ClaudeModels enum
# ---------------------------------------------------------------------------

class TestClaudeModels:
    def test_all_models_have_alias(self):
        for m in ClaudeModels:
            assert m.alias, f"{m.name} missing alias"

    def test_all_models_have_model_name(self):
        for m in ClaudeModels:
            assert m.model_name, f"{m.name} missing model_name"

    def test_model_aliases_list_matches_enum(self):
        assert set(model_aliases) == {m.alias for m in ClaudeModels}

    def test_claude_4_5_alias(self):
        assert ClaudeModels.CLAUDE_4_5.alias == "claude_4_5"

    def test_claude_opus_alias(self):
        assert ClaudeModels.CLAUDE_OPUS.alias == "claude_opus"

    def test_unique_aliases(self):
        aliases = [m.alias for m in ClaudeModels]
        assert len(aliases) == len(set(aliases))

    def test_unique_model_names(self):
        names = [m.model_name for m in ClaudeModels]
        assert len(names) == len(set(names))


# ---------------------------------------------------------------------------
# get_anthropic_completion — mocked
# ---------------------------------------------------------------------------

def _make_bedrock_response(text: str) -> dict:
    return {
        "output": {"message": {"content": [{"text": text}]}},
        "usage": {"inputTokens": 10, "outputTokens": 5},
        "stopReason": "end_turn",
    }


class TestGetAnthropicCompletion:
    def _patch_session(self, text: str):
        mock_client = mock.MagicMock()
        mock_client.converse.return_value = _make_bedrock_response(text)
        mock_session = mock.MagicMock()
        mock_session.client.return_value = mock_client
        return mock.patch("generator.aicore_llm_access.Session", return_value=mock_session)

    def test_returns_string(self):
        with self._patch_session("Hello world"):
            result = get_anthropic_completion(
                messages=[{"role": "user", "content": "Hi"}],
                model="claude_4_5",
            )
        assert result == "Hello world"

    def test_invalid_model_raises(self):
        with pytest.raises(ValueError, match="Model name must be one of"):
            get_anthropic_completion(model="nonexistent_model")

    def test_system_messages_separated(self):
        """System messages must not appear in the converse messages list."""
        captured = {}
        mock_client = mock.MagicMock()

        def capture_converse(**kwargs):
            captured.update(kwargs)
            return _make_bedrock_response("ok")

        mock_client.converse.side_effect = capture_converse
        mock_session = mock.MagicMock()
        mock_session.client.return_value = mock_client

        with mock.patch("generator.aicore_llm_access.Session", return_value=mock_session):
            get_anthropic_completion(
                messages=[
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Hello"},
                ],
                model="claude_4_5",
            )

        # system goes to separate kwarg, not messages list
        assert "system" in captured
        user_roles = [m["role"] for m in captured["messages"]]
        assert "system" not in user_roles

    def test_timeout_raises(self):
        """A hung converse call should raise RuntimeError after timeout."""
        import threading
        import time

        def _hang(**kwargs):
            time.sleep(999)

        mock_client = mock.MagicMock()
        mock_client.converse.side_effect = _hang
        mock_session = mock.MagicMock()
        mock_session.client.return_value = mock_client

        with mock.patch("generator.aicore_llm_access.Session", return_value=mock_session):
            with mock.patch("generator.aicore_llm_access.REQUEST_TIMEOUT_SEC", 0.05):
                with pytest.raises(RuntimeError, match="timed out"):
                    get_anthropic_completion(
                        messages=[{"role": "user", "content": "Hi"}],
                        model="claude_4_5",
                    )


# ---------------------------------------------------------------------------
# AICoreAnthropicLLM message formatting
# ---------------------------------------------------------------------------

class TestAICoreAnthropicLLMFormatMessages:
    @pytest.fixture
    def llm(self):
        from generator.aicore_llm import AICoreAnthropicLLM
        with mock.patch("generator.aicore_llm.Session"):
            return AICoreAnthropicLLM(model_name="claude_4_5")

    def test_plain_user_message(self, llm):
        sys_msgs, conv_msgs = llm._format_messages("hello", [])
        assert sys_msgs == []
        assert conv_msgs == [{"role": "user", "content": [{"text": "hello"}]}]

    def test_system_message_extracted(self, llm):
        history = [{"role": "system", "content": "Be concise."}]
        sys_msgs, conv_msgs = llm._format_messages("hi", history)
        assert sys_msgs == [{"text": "Be concise."}]
        assert all(m["role"] != "system" for m in conv_msgs)

    def test_conversation_history_preserved(self, llm):
        history = [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "second"},
        ]
        sys_msgs, conv_msgs = llm._format_messages("third", history)
        assert len(conv_msgs) == 3
        assert conv_msgs[0]["role"] == "user"
        assert conv_msgs[1]["role"] == "assistant"
        assert conv_msgs[2]["role"] == "user"

    def test_list_content_converted(self, llm):
        history = [{"role": "user", "content": [{"text": "block"}]}]
        _, conv_msgs = llm._format_messages("next", history)
        assert conv_msgs[0]["content"] == [{"text": "block"}]

    def test_unknown_model_raises(self):
        from generator.aicore_llm import AICoreAnthropicLLM
        with mock.patch("generator.aicore_llm.Session"):
            with pytest.raises(ValueError, match="Unknown model"):
                AICoreAnthropicLLM(model_name="invalid_model")

    def test_get_model_context_limit(self, llm):
        assert llm.get_model_context_limit() == 200_000

    def test_get_model_output_limit(self, llm):
        assert llm.get_model_output_limit() == 32_000


# ---------------------------------------------------------------------------
# _extract_action (generate_harbor_solutions)
# ---------------------------------------------------------------------------

class TestExtractAction:
    def test_command_extracted(self):
        result = _extract_action("<think>plan</think><command>ls -la</command>")
        assert result == {"type": "command", "command": "ls -la"}

    def test_done_action_tag(self):
        result = _extract_action("<think>done</think><action>done</action>")
        assert result["type"] == "done"

    def test_done_in_command_tag(self):
        result = _extract_action("<command>done</command>")
        assert result["type"] == "done"

    def test_invalid_response(self):
        result = _extract_action("just some text with no tags")
        assert result["type"] == "invalid"

    def test_multiline_command(self):
        result = _extract_action("<command>echo hello\\\nworld</command>")
        assert result["type"] == "command"
        assert "echo" in result["command"]

    def test_case_insensitive_done(self):
        result = _extract_action("<ACTION>DONE</ACTION>")
        assert result["type"] == "done"

    def test_last_command_wins(self):
        result = _extract_action("<command>first</command><command>second</command>")
        assert result["command"] == "second"


# ---------------------------------------------------------------------------
# compute_pass_at_k
# ---------------------------------------------------------------------------

class TestPassAtK:
    def test_zero_correct(self):
        result = compute_pass_at_k(n=5, c=0)
        assert all(v == 0.0 for v in result.values())

    def test_all_correct(self):
        result = compute_pass_at_k(n=5, c=5)
        assert all(v == 1.0 for v in result.values())

    def test_pass_at_1_partial(self):
        result = compute_pass_at_k(n=4, c=2)
        assert 0.0 < result[1] < 1.0

    def test_keys_range(self):
        result = compute_pass_at_k(n=3, c=1)
        assert set(result.keys()) == {1, 2, 3}

    def test_monotone_increasing(self):
        result = compute_pass_at_k(n=5, c=2)
        values = [result[k] for k in sorted(result)]
        assert values == sorted(values)
