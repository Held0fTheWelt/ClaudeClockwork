"""Ollama model management skill: list, get, set, validate — canonical state, no scripts."""
from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.core.ollama import (
    OllamaModelManager,
    OllamaUnavailableError,
    ModelNotFoundError,
)


class OllamaModelManageSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        root = kwargs.get("root") or context.working_directory
        action = (kwargs.get("action") or "get").strip().lower()
        model = (kwargs.get("model") or "").strip()
        manager = OllamaModelManager(project_root=Path(root))

        if action == "list":
            return self._action_list(manager)
        if action == "get":
            return self._action_get(manager)
        if action == "set":
            return self._action_set(manager, model)
        if action == "validate":
            return self._action_validate(manager, model)
        if action == "profiles":
            return self._action_profiles(manager)
        return SkillResult(
            False,
            "ollama_model_manage",
            error=f"Unknown action: {action!r}. Use one of: list, get, set, validate, profiles",
            data={"action": action},
        )

    def _action_list(self, manager: OllamaModelManager) -> SkillResult:
        try:
            models = manager.list_models()
            default_model = manager.get_global_default()
            return SkillResult(
                True,
                "ollama_model_manage",
                data={
                    "action": "list",
                    "available_models": models,
                    "active_model": default_model,
                    "default_model": default_model,
                    "message": f"Found {len(models)} model(s). Global default: {default_model}",
                },
            )
        except OllamaUnavailableError as e:
            return SkillResult(
                False,
                "ollama_model_manage",
                error=str(e),
                data={"action": "list", "available_models": [], "message": str(e)},
            )

    def _action_get(self, manager: OllamaModelManager) -> SkillResult:
        try:
            default_model = manager.get_global_default()
            return SkillResult(
                True,
                "ollama_model_manage",
                data={
                    "action": "get",
                    "active_model": default_model,
                    "default_model": default_model,
                    "message": f"Global default Ollama model: {default_model}",
                },
            )
        except Exception as e:
            return SkillResult(
                False,
                "ollama_model_manage",
                error=str(e),
                data={"action": "get", "message": str(e)},
            )

    def _action_set(self, manager: OllamaModelManager, model: str) -> SkillResult:
        if not model:
            return SkillResult(
                False,
                "ollama_model_manage",
                error="Missing 'model' for action=set",
                data={"action": "set"},
            )
        try:
            set_model = manager.set_active_model(model)
            return SkillResult(
                True,
                "ollama_model_manage",
                data={
                    "action": "set",
                    "active_model": set_model,
                    "message": f"Active Ollama model set to: {set_model}",
                },
            )
        except OllamaUnavailableError as e:
            return SkillResult(False, "ollama_model_manage", error=str(e), data={"action": "set"})
        except ModelNotFoundError as e:
            return SkillResult(False, "ollama_model_manage", error=str(e), data={"action": "set"})

    def _action_validate(self, manager: OllamaModelManager, model: str) -> SkillResult:
        if not model:
            return SkillResult(
                False,
                "ollama_model_manage",
                error="Missing 'model' for action=validate",
                data={"action": "validate"},
            )
        ok, msg = manager.validate_model(model)
        return SkillResult(
            ok,
            "ollama_model_manage",
            data={"action": "validate", "model": model, "valid": ok, "message": msg},
            error=None if ok else msg,
        )

    def _action_profiles(self, manager: OllamaModelManager) -> SkillResult:
        """Return configured profiles (model, prompt_budget_chars, num_ctx_tokens per profile)."""
        profiles = manager.get_profiles()
        default_model = manager.get_global_default()
        return SkillResult(
            True,
            "ollama_model_manage",
            data={
                "action": "profiles",
                "profiles": profiles,
                "default_model": default_model,
                "message": f"Profiles: {list(profiles.keys())}; global default: {default_model}",
            },
        )
