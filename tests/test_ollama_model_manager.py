"""Tests for Ollama model manager and ollama_model_manage skill."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure .claude is on path for skill import (skills.localai.ollama_model_manage)
_REPO_ROOT = Path(__file__).resolve().parents[1]
_CLAUDE = _REPO_ROOT / ".claude"
if _CLAUDE.exists() and str(_CLAUDE) not in sys.path:
    sys.path.insert(0, str(_CLAUDE))

from claudeclockwork.core.ollama import (
    OllamaModelManager,
    OllamaUnavailableError,
    ModelNotFoundError,
)


@pytest.fixture
def temp_project(tmp_path):
    """Project root with .claude/state and optional config."""
    (tmp_path / ".claude" / "state").mkdir(parents=True)
    (tmp_path / ".claude" / "config").mkdir(parents=True)
    return tmp_path


class TestOllamaModelManager:
    """Tests for OllamaModelManager with mocked Ollama API."""

    def test_list_models_success(self, temp_project):
        """list_models returns names when API responds."""
        mock_data = {"models": [{"name": "qwen2.5-coder:14b"}, {"name": "phi4:14b"}]}
        with patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data).encode()
            manager = OllamaModelManager(project_root=temp_project)
            models = manager.list_models()
        assert models == ["qwen2.5-coder:14b", "phi4:14b"]

    def test_list_models_unavailable(self, temp_project):
        """list_models raises OllamaUnavailableError when API fails."""
        with patch("urllib.request.urlopen") as m:
            m.side_effect = OSError("Connection refused")
            manager = OllamaModelManager(project_root=temp_project)
            with pytest.raises(OllamaUnavailableError) as exc_info:
                manager.list_models()
        assert "not available" in str(exc_info.value).lower() or "reachable" in str(exc_info.value).lower()

    def test_get_active_model_from_state(self, temp_project):
        """get_global_default returns value from state file (default_model or legacy active_model)."""
        state_file = temp_project / ".claude" / "state" / "ollama_model_state.json"
        state_file.write_text(json.dumps({"default_model": "phi4:14b", "last_updated_by": "test"}))
        with patch.object(OllamaModelManager, "list_models"):
            manager = OllamaModelManager(project_root=temp_project)
            assert manager.get_global_default() == "phi4:14b"
            assert manager.get_active_model() == "phi4:14b"

    def test_get_active_model_fallback_config(self, temp_project):
        """get_active_model uses config default when no state file."""
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("default_model: qwen2.5-coder:32b\n")
        manager = OllamaModelManager(project_root=temp_project)
        with patch.object(OllamaModelManager, "list_models"):
            assert manager.get_active_model() == "qwen2.5-coder:32b"

    def test_set_active_model_valid_persists(self, temp_project):
        """set_active_model validates via tags, then persists default_model to state file."""
        mock_data = {"models": [{"name": "qwen2.5-coder:14b"}]}
        with patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data).encode()
            manager = OllamaModelManager(project_root=temp_project)
            out = manager.set_active_model("qwen2.5-coder:14b")
        assert out == "qwen2.5-coder:14b"
        state = json.loads((temp_project / ".claude" / "state" / "ollama_model_state.json").read_text())
        assert state["default_model"] == "qwen2.5-coder:14b"

    def test_set_active_model_not_found_raises(self, temp_project):
        """set_active_model raises ModelNotFoundError when model not available."""
        mock_data = {"models": [{"name": "other:7b"}]}
        with patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data).encode()
            manager = OllamaModelManager(project_root=temp_project)
            with pytest.raises(ModelNotFoundError) as exc_info:
                manager.set_active_model("qwen2.5-coder:14b")
        assert "not available" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_validate_model_available(self, temp_project):
        """validate_model returns (True, msg) when model is available."""
        mock_data = {"models": [{"name": "phi4:14b"}]}
        with patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data).encode()
            manager = OllamaModelManager(project_root=temp_project)
            ok, msg = manager.validate_model("phi4:14b")
        assert ok is True
        assert "available" in msg.lower() or "resolves" in msg.lower()

    def test_validate_model_unavailable_ollama(self, temp_project):
        """validate_model returns (False, msg) when Ollama is unreachable."""
        with patch("urllib.request.urlopen") as m:
            m.side_effect = OSError("Connection refused")
            manager = OllamaModelManager(project_root=temp_project)
            ok, msg = manager.validate_model("phi4:14b")
        assert ok is False
        assert "not available" in msg.lower() or "connection" in msg.lower() or "refused" in msg.lower()

    def test_resolve_model_override_wins(self, temp_project):
        """resolve_model: per_invocation_override > profile > state > config."""
        (temp_project / ".claude" / "state" / "ollama_model_state.json").write_text(
            json.dumps({"default_model": "global:14b"})
        )
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
default_model: "global:14b"
profiles:
  implementation:
    model: "impl:32b"
""")
        manager = OllamaModelManager(project_root=temp_project)
        model, source = manager.resolve_model(override="override:7b", profile="implementation")
        assert model == "override:7b"
        assert source == "per_invocation_override"

    def test_resolve_model_profile_over_global(self, temp_project):
        """resolve_model: profile model used when no override."""
        (temp_project / ".claude" / "state" / "ollama_model_state.json").write_text(
            json.dumps({"default_model": "global:14b"})
        )
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
default_model: "global:14b"
profiles:
  review:
    model: "review:14b"
""")
        manager = OllamaModelManager(project_root=temp_project)
        model, source = manager.resolve_model(override=None, profile="review")
        assert model == "review:14b"
        assert source == "profile_model"

    def test_resolve_model_state_default_over_config(self, temp_project):
        """resolve_model: state.default_model used when present, else config.default_model."""
        (temp_project / ".claude" / "state" / "ollama_model_state.json").write_text(
            json.dumps({"default_model": "state-model:14b"})
        )
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text('default_model: "config-model:14b"\n')
        manager = OllamaModelManager(project_root=temp_project)
        model, source = manager.resolve_model(override=None, profile=None)
        assert model == "state-model:14b"
        assert source == "state_default_model"

    def test_resolve_model_global_when_no_profile_model(self, temp_project):
        """resolve_model: global default when profile has no model (e.g. execution)."""
        (temp_project / ".claude" / "state" / "ollama_model_state.json").write_text(
            json.dumps({"default_model": "global:14b"})
        )
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
default_model: "global:14b"
profiles:
  default:
    prompt_budget_chars: 32000
  execution:
    prompt_budget_chars: 8000
""")
        manager = OllamaModelManager(project_root=temp_project)
        model, source = manager.resolve_model(override=None, profile="execution")
        assert model == "global:14b"
        assert source in ("state_default_model", "config_default_model")

    def test_get_prompt_budget_profile_over_global(self, temp_project):
        """get_prompt_budget: profile prompt_budget_chars overrides global."""
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
global_prompt_budget_chars: 64000
profiles:
  implementation:
    prompt_budget_chars: 24000
""")
        manager = OllamaModelManager(project_root=temp_project)
        assert manager.get_prompt_budget(profile="implementation") == 24000
        assert manager.get_prompt_budget(profile=None) == 64000

    def test_get_num_ctx_profile_over_global(self, temp_project):
        """get_num_ctx: profile num_ctx_tokens overrides global."""
        (temp_project / ".claude" / "config" / "ollama.yaml").write_text("""
global_num_ctx_tokens: 8192
profiles:
  planning:
    num_ctx_tokens: 4096
""")
        manager = OllamaModelManager(project_root=temp_project)
        assert manager.get_num_ctx(profile="planning") == 4096
        assert manager.get_num_ctx(profile=None) == 8192

    def test_alias_resolution_via_tags(self, temp_project):
        """validate_model and set_active_model resolve alias to installed tag via /api/tags only."""
        mock_data = {"models": [{"name": "qwen2.5-14b:research-q4_0"}]}
        with patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data).encode()
            manager = OllamaModelManager(project_root=temp_project)
            ok, msg = manager.validate_model("qwen2.5-14b:research")
        assert ok is True
        assert "qwen2.5-14b:research" in msg or "resolves" in msg.lower()

    def test_validate_reject_unknown_model(self, temp_project):
        """validate_model returns False for model not in tags; no show/pull."""
        mock_data = {"models": [{"name": "other:7b"}]}
        with patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data).encode()
            manager = OllamaModelManager(project_root=temp_project)
            ok, msg = manager.validate_model("nonexistent:99b")
        assert ok is False
        assert "not found" in msg.lower() or "available" in msg.lower()


class TestOllamaModelManageSkill:
    """Tests for ollama_model_manage skill (direct class and manifest)."""

    def test_skill_manifest_exists_and_has_entrypoint(self):
        """ollama_model_manage manifest exists and has required entrypoint."""
        project_root = Path(__file__).resolve().parents[1]
        manifest_path = project_root / ".claude" / "skills" / "localai" / "ollama_model_manage" / "manifest.json"
        assert manifest_path.exists()
        data = json.loads(manifest_path.read_text())
        assert data.get("name") == "ollama_model_manage"
        assert "entrypoint" in data
        assert "ollama" in data.get("description", "").lower() or "model" in data.get("description", "").lower()

    def test_skill_get_action_returns_active_model(self, temp_project):
        """Skill action=get returns active model from state/fallback."""
        from claudeclockwork.core.models.execution_context import ExecutionContext
        from claudeclockwork.core.models.skill_result import SkillResult
        # Load skill class from file (avoids registry/build_registry loading all manifests)
        import importlib.util
        skill_path = _REPO_ROOT / ".claude" / "skills" / "localai" / "ollama_model_manage" / "skill.py"
        spec = importlib.util.spec_from_file_location("ollama_model_manage_skill", skill_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        OllamaModelManageSkill = mod.OllamaModelManageSkill
        (temp_project / ".claude" / "state" / "ollama_model_state.json").write_text(
            json.dumps({"default_model": "test-model:1b"})
        )
        ctx = ExecutionContext(request_id="t1", user_input="get", working_directory=str(temp_project))
        skill = OllamaModelManageSkill()
        result = skill.run(ctx, action="get", root=str(temp_project))
        assert isinstance(result, SkillResult)
        assert result.success is True
        assert result.data.get("active_model") == "test-model:1b"
        assert result.data.get("default_model") == "test-model:1b"

    def test_skill_unknown_action_fails(self, temp_project):
        """Skill with unknown action returns failure."""
        from claudeclockwork.core.models.execution_context import ExecutionContext
        from claudeclockwork.core.models.skill_result import SkillResult
        import importlib.util
        skill_path = _REPO_ROOT / ".claude" / "skills" / "localai" / "ollama_model_manage" / "skill.py"
        spec = importlib.util.spec_from_file_location("ollama_model_manage_skill", skill_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        OllamaModelManageSkill = mod.OllamaModelManageSkill
        ctx = ExecutionContext(request_id="t2", user_input="unknown", working_directory=str(temp_project))
        skill = OllamaModelManageSkill()
        result = skill.run(ctx, action="unknown_act", root=str(temp_project))
        assert isinstance(result, SkillResult)
        assert result.success is False
        assert "Unknown action" in (result.error or "")
