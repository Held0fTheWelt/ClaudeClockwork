from __future__ import annotations

import json
import re
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.runtime import build_registry

_HAS_RUN_RE = re.compile(r'^def\s+run\s*\(', re.MULTILINE)


class CapabilityMapBuildSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        out_rel = kwargs.get("out", "validation_runs/capability_map.json")
        out_path = (repo_root / out_rel).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        registry = build_registry(repo_root)
        manifest_skills = [
            {
                "skill_id": m.name,
                "category": m.category,
                "description": m.description,
                "entrypoint": m.entrypoint,
                "legacy_bridge": bool(m.metadata.get("legacy_bridge")),
            }
            for m in registry.list_skills(enabled_only=False)
        ]

        legacy_skills: list[dict] = []
        skills_dir = repo_root / ".claude" / "tools" / "skills"
        if skills_dir.exists():
            for p in sorted(skills_dir.glob("*.py")):
                if p.name in {"__init__.py", "skill_runner.py"}:
                    continue
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                if not _HAS_RUN_RE.search(txt):
                    continue
                hint = next((ln.strip(" #") for ln in txt.splitlines() if ln.strip(" #")), "")
                legacy_skills.append({"skill_id": p.stem, "hint": hint[:160]})

        agents: list[dict] = []
        agents_dir = repo_root / ".claude" / "agents"
        if agents_dir.exists():
            agents = [{"agent": p.stem, "path": str(p.relative_to(repo_root))} for p in sorted(agents_dir.rglob("*.md"))]

        cap_map = {
            "type": "capability_map",
            "project_root": str(repo_root),
            "skills": {"manifest": manifest_skills, "legacy": legacy_skills},
            "agents": agents,
        }
        out_path.write_text(json.dumps(cap_map, indent=2, ensure_ascii=False), encoding="utf-8")

        return SkillResult(
            True,
            "capability_map_build",
            data={
                "out": str(out_path),
                "manifest_skills": len(manifest_skills),
                "legacy_skills": len(legacy_skills),
                "agents": len(agents),
            },
        )
