from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.runtime import build_registry


def _get_legacy_skill_ids(repo_root: Path) -> set[str]:
    skills_dir = repo_root / ".claude" / "tools" / "skills"
    if not skills_dir.exists():
        return set()
    ids = set()
    for p in skills_dir.glob("*.py"):
        if p.name not in {"__init__.py", "skill_runner.py"}:
            ids.add(p.stem)
    return ids


_PRIORITY: dict[str, int] = {
    "qa": 1,
    "evidence": 1,
    "docs": 2,
    "meta": 2,
    "planning": 3,
    "ops": 3,
    "misc": 4,
    "performance": 4,
    "routing": 5,
}


class ParityScanAndMvpPlannerSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()

        legacy_ids = _get_legacy_skill_ids(repo_root)
        registry = build_registry(repo_root)
        manifest_ids = {m.name for m in registry.list_skills(enabled_only=False)}

        wrapped = legacy_ids & manifest_ids
        unwrapped = legacy_ids - manifest_ids
        manifest_only = manifest_ids - legacy_ids

        wrap_candidates = sorted(
            [{"skill_id": s, "priority": _PRIORITY.get("misc", 4)} for s in unwrapped],
            key=lambda x: (x["priority"], x["skill_id"]),
        )

        total = len(legacy_ids) or 1
        parity_percent = round(len(wrapped) / total * 100, 1)

        return SkillResult(
            True,
            "parity_scan_and_mvp_planner",
            data={
                "legacy_count": len(legacy_ids),
                "manifest_count": len(manifest_ids),
                "wrapped_count": len(wrapped),
                "unwrapped_count": len(unwrapped),
                "manifest_only_count": len(manifest_only),
                "parity_percent": parity_percent,
                "wrap_candidates": wrap_candidates,
                "manifest_only": sorted(manifest_only),
            },
        )
