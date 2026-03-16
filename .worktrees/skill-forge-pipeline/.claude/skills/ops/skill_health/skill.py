"""Phase 16 — skill_health: audit all manifest skills for health issues."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

_REQUIRED_KEYS = {"id", "category", "description", "entrypoint"}


def _check_manifest(manifest_path: Path, root: Path) -> list[dict]:
    issues: list[dict] = []
    skill_id = manifest_path.parent.name

    # invalid_manifest
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        issues.append({"skill_id": skill_id, "issue_type": "invalid_manifest", "detail": str(e)})
        return issues

    # missing_metadata
    missing = _REQUIRED_KEYS - set(data.keys())
    if missing:
        issues.append({
            "skill_id": skill_id,
            "issue_type": "missing_metadata",
            "detail": f"Missing keys: {sorted(missing)}",
        })

    # missing_bridge
    legacy_bridge = data.get("metadata", {}).get("legacy_bridge")
    if legacy_bridge and isinstance(legacy_bridge, str):
        bridge_path = root / ".claude" / "tools" / "skills" / f"{legacy_bridge}.py"
        if not bridge_path.exists():
            issues.append({
                "skill_id": skill_id,
                "issue_type": "missing_bridge",
                "detail": f"Bridge file not found: {bridge_path.relative_to(root)}",
            })

    # bad_entrypoint
    entrypoint = data.get("entrypoint", "")
    if entrypoint and ":" in entrypoint:
        module_path = entrypoint.split(":")[0]
        # Ensure .claude is on sys.path for skills.* imports
        claude_path = str(root / ".claude")
        root_str = str(root)
        added = []
        for p in [root_str, claude_path]:
            if p not in sys.path:
                sys.path.insert(0, p)
                added.append(p)
        try:
            importlib.import_module(module_path)
        except Exception as e:
            issues.append({
                "skill_id": skill_id,
                "issue_type": "bad_entrypoint",
                "detail": str(e),
            })
        finally:
            for p in added:
                if p in sys.path:
                    sys.path.remove(p)

    return issues


class SkillHealthSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        root = Path(kwargs.get("root", context.working_directory)).resolve()
        skills_root = root / ".claude" / "skills"

        manifest_paths = sorted(skills_root.rglob("manifest.json"))
        all_issues: list[dict] = []
        skill_ids_with_issues: set[str] = set()

        for mp in manifest_paths:
            issues = _check_manifest(mp, root)
            if issues:
                skill_ids_with_issues.add(mp.parent.name)
                all_issues.extend(issues)

        total = len(manifest_paths)
        unhealthy = len(skill_ids_with_issues)
        healthy = total - unhealthy

        return SkillResult(True, "skill_health", data={
            "total": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "issues": all_issues,
        })
