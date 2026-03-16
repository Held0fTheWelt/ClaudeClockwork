"""Tests for OllamaAgent: managed model, profile resolution, override no-mutate, context budget."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.core.agents.ollama_agent import OllamaAgent


@pytest.fixture
def temp_project(tmp_path):
    (tmp_path / ".claude" / "state").mkdir(parents=True)
    (tmp_path / ".claude" / "config").mkdir(parents=True)
    return tmp_path


class TestOllamaAgentManagedModel:
    """OllamaAgent resolves model: override > profile > global."""

    def test_agent_uses_managed_model_when_model_none(self, temp_project):
        """When model=None, agent uses global default from state or config."""
        state_file = temp_project / ".claude" / "state" / "ollama_model_state.json"
        state_file.write_text(
            json.dumps({"default_model": "qwen2.5-coder:14b", "last_updated_by": "test"})
        )
        agent = OllamaAgent(model=None, project_root=temp_project)
        assert agent.model == "qwen2.5-coder:14b"
        assert agent._model_source in ("state_default_model", "config_default_model")

    def test_agent_explicit_model_overrides_state(self, temp_project):
        """When model is set, it overrides state (per-invocation override)."""
        state_file = temp_project / ".claude" / "state" / "ollama_model_state.json"
        state_file.write_text(
            json.dumps({"default_model": "other:7b", "last_updated_by": "test"})
        )
        agent = OllamaAgent(model="phi4:14b", project_root=temp_project)
        assert agent.model == "phi4:14b"
        assert agent._model_source == "per_invocation_override"

    def test_per_call_override_does_not_mutate_state(self, temp_project):
        """Per-call override must not change persistent state."""
        state_file = temp_project / ".claude" / "state" / "ollama_model_state.json"
        state_file.write_text(
            json.dumps({"default_model": "global-model:14b", "last_updated_by": "test"})
        )
        agent = OllamaAgent(model="override-model:7b", project_root=temp_project)
        assert agent.model == "override-model:7b"
        state_after = json.loads(state_file.read_text())
        assert state_after.get("default_model") == "global-model:14b"

    def test_agent_profile_uses_profile_model_when_no_override(self, temp_project):
        """When profile is set and has model, use profile model (no override)."""
        (temp_project / ".claude" / "state" / "ollama_model_state.json").write_text(
            json.dumps({"default_model": "global-default:14b", "last_updated_by": "test"})
        )
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
default_model: "global-default:14b"
profiles:
  implementation:
    model: "qwen2.5-coder:32b"
    prompt_budget_chars: 24000
""")
        agent = OllamaAgent(model=None, profile="implementation", project_root=temp_project)
        assert agent.model == "qwen2.5-coder:32b"
        assert agent._model_source == "profile_model"

    def test_agent_override_beats_profile(self, temp_project):
        """Per-invocation override beats profile-configured model."""
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
default_model: "global:14b"
profiles:
  review:
    model: "review-model:14b"
""")
        agent = OllamaAgent(model="explicit:7b", profile="review", project_root=temp_project)
        assert agent.model == "explicit:7b"
        assert agent._model_source == "per_invocation_override"

    def test_agent_fallback_when_no_state(self, temp_project):
        """When no state file, agent uses config or code fallback."""
        agent = OllamaAgent(model=None, project_root=temp_project)
        assert agent.model is not None
        assert isinstance(agent.model, str)
        assert len(agent.model) > 0
