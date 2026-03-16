from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.runtime import build_registry


class SkillRegistrySearchSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        query = str(kwargs.get("query") or "").strip()
        max_results = int(kwargs.get("max_results") or 25)

        if not query:
            return SkillResult(False, "skill_registry_search", error="inputs.query is required")

        registry = build_registry(repo_root)
        manifest_matches = registry.search(query, enabled_only=False)
        manifest_hits = [
            {
                "name": m.name,
                "category": m.category,
                "description": m.description,
                "tags": m.tags,
                "type": "manifest",
            }
            for m in manifest_matches[:max_results]
        ]

        query_tokens = set(query.replace("_", " ").split())
        legacy_hits: list[dict] = []
        skills_dir = repo_root / ".claude" / "tools" / "skills"
        if skills_dir.exists():
            for py_path in sorted(skills_dir.glob("*.py")):
                if py_path.name in {"__init__.py", "skill_runner.py"}:
                    continue
                text = py_path.read_text(encoding="utf-8", errors="ignore")
                first_line = next((ln.strip(" #") for ln in text.splitlines() if ln.strip(" #")), "")
                corpus = f"{py_path.stem} {first_line}".lower()
                score = sum(1 for t in query_tokens if t and t in corpus)
                if score > 0:
                    legacy_hits.append({"name": py_path.stem, "description": first_line[:120], "type": "legacy"})
            legacy_hits = legacy_hits[:max_results]

        return SkillResult(
            True,
            "skill_registry_search",
            data={
                "query": query,
                "manifest_hits": manifest_hits,
                "legacy_hits": legacy_hits,
                "summary": {"manifest_matches": len(manifest_hits), "legacy_matches": len(legacy_hits)},
            },
        )
