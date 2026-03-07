"""Phase 38 — kb.explain skill: answer plus file path citations."""
from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class KbExplainSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        try:
            from claudeclockwork.kb.retrieval import explain
            repo = Path(context.working_directory).resolve()
            kb_root = repo / ".clockwork_runtime" / "kb"
            question = kwargs.get("question") or ""
            top_k = int(kwargs.get("top_k") or 3)
            out = explain(kb_root, question, top_k=top_k)
            return SkillResult(True, "kb_explain", output=out)
        except Exception as e:
            return SkillResult(False, "kb_explain", error=str(e))
