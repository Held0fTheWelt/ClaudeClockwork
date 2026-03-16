"""Tests for Ollama context budget and profile-aware prompt building."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from claudeclockwork.core.ollama.context_budget import (
    apply_budget,
    ContextBudgetExceededError,
)
from claudeclockwork.core.ollama import OllamaModelManager
from claudeclockwork.core.agents.ollama_agent import OllamaAgent


@pytest.fixture
def temp_project(tmp_path):
    (tmp_path / ".claude" / "state").mkdir(parents=True)
    (tmp_path / ".claude" / "config").mkdir(parents=True)
    return tmp_path


class TestApplyBudget:
    """apply_budget enforces character limit with configurable strategy."""

    def test_under_budget_unchanged(self):
        text = "short"
        assert apply_budget(text, 100) == text

    def test_truncate_tail(self):
        text = "a" * 200
        out = apply_budget(text, 50, strategy="truncate_tail")
        assert len(out) <= 50 + 25  # 50 + len(ellipsis)
        assert out.endswith("... truncated ...") or "truncated" in out

    def test_truncate_head(self):
        text = "a" * 200
        out = apply_budget(text, 50, strategy="truncate_head")
        assert len(out) <= 50 + 25
        assert out.startswith("...") or "truncated" in out

    def test_reject_raises_when_over_budget(self):
        text = "a" * 200
        with pytest.raises(ContextBudgetExceededError) as exc_info:
            apply_budget(text, 50, strategy="reject")
        assert "200" in str(exc_info.value) and "50" in str(exc_info.value)

    def test_reject_passes_when_under_budget(self):
        text = "short"
        assert apply_budget(text, 100, strategy="reject") == text

    def test_slice_lines_under_budget_unchanged(self):
        text = "line1\nline2\nline3"
        assert apply_budget(text, 1000, strategy="slice_lines") == text


class TestProfilePromptBudget:
    """Profile and global prompt_budget_chars are applied correctly."""

    def test_get_prompt_budget_from_profile(self, temp_project):
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
global_prompt_budget_chars: 64000
profiles:
  implementation:
    prompt_budget_chars: 24000
  review:
    prompt_budget_chars: 16000
""")
        manager = OllamaModelManager(project_root=temp_project)
        assert manager.get_prompt_budget(profile="implementation") == 24000
        assert manager.get_prompt_budget(profile="review") == 16000

    def test_get_prompt_budget_fallback_global(self, temp_project):
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
global_prompt_budget_chars: 32000
profiles:
  implementation:
    model: "qwen2.5-coder:32b"
""")
        manager = OllamaModelManager(project_root=temp_project)
        # profile has no prompt_budget_chars -> global
        assert manager.get_prompt_budget(profile="implementation") == 32000

    def test_get_prompt_budget_no_config_uses_default(self, temp_project):
        manager = OllamaModelManager(project_root=temp_project)
        assert manager.get_prompt_budget() == 12_000


class TestAgentContextBounded:
    """OllamaAgent sends bounded prompt to Ollama when over budget."""

    def test_agent_reason_uses_bounded_prompt(self, temp_project):
        """reason() truncates full_prompt to budget before calling Ollama."""
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
default_model: "qwen2.5-coder:14b"
profiles:
  default:
    prompt_budget_chars: 100
""")
        (temp_project / ".claude" / "state" / "ollama_model_state.json").write_text(
            json.dumps({"default_model": "qwen2.5-coder:14b"})
        )
        agent = OllamaAgent(model=None, profile="default", project_root=temp_project)
        # Without bounding, this would be 500 chars; budget 100
        huge_context = "x" * 500
        with patch("claudeclockwork.core.agents.ollama_agent.subprocess.run") as m:
            m.return_value.returncode = 0
            m.return_value.stdout = "ok"
            m.return_value.stderr = ""
            agent.reason("task", context=huge_context, verbose=False)
        assert m.called
        input_sent = m.call_args.kwargs.get("input", "")
        assert len(input_sent) <= 100 + 50  # budget + ellipsis