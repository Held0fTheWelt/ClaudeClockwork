"""Phase 20 — localai_run: generic capability runner skill."""
from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.localai import run_local_capability, validate_local_tool_result


class LocalaiRunSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        capability = (kwargs.get("capability") or "").strip()
        inputs = kwargs.get("inputs") or {}
        root = kwargs.get("root") or context.working_directory
        if not capability:
            return SkillResult(False, "localai_run", error="Missing 'capability'", data={"errors": [{"code": "missing_input", "message": "capability required"}]})
        result = run_local_capability(capability, inputs, project_root=Path(root))
        valid, errs = validate_local_tool_result(result)
        if not valid:
            return SkillResult(False, "localai_run", error="; ".join(errs), data=result)
        success = result.get("status") == "ok"
        return SkillResult(success, "localai_run", data=result, error=None if success else (result.get("errors") or [{}])[0].get("message"))
