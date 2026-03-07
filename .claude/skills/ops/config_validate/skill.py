"""Phase 16 — config_validate: parse all JSON/YAML config files and report errors."""
from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


def _try_load_yaml(text: str) -> str | None:
    """Return error string if YAML fails to load, else None."""
    try:
        import yaml  # type: ignore
        yaml.safe_load(text)
        return None
    except ImportError:
        # If yaml is not installed, skip YAML validation
        return None
    except Exception as e:
        return str(e)


class ConfigValidateSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        root = Path(context.working_directory).resolve()
        config_path_strs: list[str] = kwargs.get(
            "config_paths", [".claude/config/", "configs/"]
        )
        config_paths = [(root / p) for p in config_path_strs]

        files_checked = 0
        valid = 0
        issues: list[dict] = []

        for cp in config_paths:
            if not cp.exists():
                continue
            candidates = list(cp.rglob("*.json")) + list(cp.rglob("*.yaml")) + list(cp.rglob("*.yml"))
            for f in sorted(candidates):
                files_checked += 1
                try:
                    text = f.read_text(encoding="utf-8")
                except Exception as e:
                    issues.append({"path": str(f.relative_to(root)), "error": f"read error: {e}"})
                    continue

                error: str | None = None
                if f.suffix.lower() == ".json":
                    try:
                        json.loads(text)
                    except json.JSONDecodeError as e:
                        error = str(e)
                elif f.suffix.lower() in (".yaml", ".yml"):
                    error = _try_load_yaml(text)

                if error:
                    issues.append({"path": str(f.relative_to(root)), "error": error})
                else:
                    valid += 1

        invalid = files_checked - valid

        return SkillResult(True, "config_validate", data={
            "files_checked": files_checked,
            "valid": valid,
            "invalid": invalid,
            "issues": issues,
        })
