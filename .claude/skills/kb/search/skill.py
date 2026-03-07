"""Phase 38 — kb.search skill: returns path, snippet, score."""
from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class KbSearchSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        try:
            from claudeclockwork.kb.retrieval import search
            repo = Path(context.working_directory).resolve()
            kb_root = repo / ".clockwork_runtime" / "kb"
            query = kwargs.get("query") or ""
            top_k = int(kwargs.get("top_k") or 5)
            results = search(kb_root, query, top_k=top_k)
            return SkillResult(True, "kb_search", output={"hits": results})
        except Exception as e:
            return SkillResult(False, "kb_search", error=str(e))
