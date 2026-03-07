"""Phase 20 — audio_asr: local speech-to-text skill."""
from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.localai import run_local_capability, validate_local_tool_result


class AudioAsrSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        path = kwargs.get("path") or kwargs.get("audio_path") or ""
        inputs = {"path": path, "audio_path": path}
        root = kwargs.get("root") or context.working_directory
        result = run_local_capability("audio.asr", inputs, project_root=Path(root))
        valid, errs = validate_local_tool_result(result)
        if not valid:
            return SkillResult(False, "audio_asr", error="; ".join(errs), data=result)
        success = result.get("status") == "ok"
        return SkillResult(success, "audio_asr", data=result, error=None if success else (result.get("errors") or [{}])[0].get("message"))
