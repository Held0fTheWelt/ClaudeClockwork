from __future__ import annotations

import os
import sys
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class ScreencastScriptSkill(SkillBase):
    _LEGACY_ID = "screencast_script"

    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        skills_root = repo_root / ".claude" / "tools" / "skills"
        if str(skills_root) not in sys.path:
            sys.path.insert(0, str(skills_root))
        try:
            module = __import__(self._LEGACY_ID)
        except Exception as exc:
            return SkillResult(False, self._LEGACY_ID, error=f"Legacy import failed: {exc}")
        req = {
            "type": "skill_request_spec",
            "request_id": context.request_id,
            "skill_id": self._LEGACY_ID,
            "inputs": kwargs,
        }
        old_cwd = Path.cwd()
        try:
            os.chdir(repo_root)
            result = module.run(req)
        except Exception as exc:
            return SkillResult(False, self._LEGACY_ID, error=f"Legacy execution failed: {exc}")
        finally:
            os.chdir(old_cwd)
        status = result.get("status") == "ok"
        outputs = result.get("outputs", {})
        errors = result.get("errors", [])
        warnings = result.get("warnings", [])
        metrics = result.get("metrics", {})
        return SkillResult(
            success=status,
            skill_name=self._LEGACY_ID,
            data=outputs,
            error=("; ".join(errors) if errors else None),
            warnings=warnings,
            metadata=metrics,
        )
