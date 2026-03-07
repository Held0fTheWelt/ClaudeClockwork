"""Phase 20 — embed_text: local text embeddings skill."""
from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.localai import run_local_capability, validate_local_tool_result


class EmbedTextSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        text = kwargs.get("text") or kwargs.get("input") or ""
        inputs = {"text": text, "input": text}
        root = kwargs.get("root") or context.working_directory
        result = run_local_capability("embed.text", inputs, project_root=Path(root))
        valid, errs = validate_local_tool_result(result)
        if not valid:
            return SkillResult(False, "embed_text", error="; ".join(errs), data=result)
        success = result.get("status") == "ok"
        return SkillResult(success, "embed_text", data=result, error=None if success else (result.get("errors") or [{}])[0].get("message"))
