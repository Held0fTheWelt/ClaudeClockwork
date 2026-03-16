from __future__ import annotations

import re
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

_CODE_FENCE_RX = re.compile(r"```")
_BROKEN_LINK_RX = re.compile(r"\[([^\]]+)\]\(\s*\)")
_DIAGRAM_RX = re.compile(r"```\s*(mermaid|diagram|plantuml|graphviz)", re.IGNORECASE)
_IMAGE_RX = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_HEADING_RX = re.compile(r"^#{1,3}\s+(.+)", re.MULTILINE)

_SCOPE_REQUIRED: dict[str, list[str]] = {
    "general": ["introduction", "usage", "examples", "reference"],
    "tutorial": ["introduction", "prerequisites", "steps", "summary"],
    "api_docs": ["overview", "authentication", "endpoints", "examples"],
    "lastenheft": ["introduction", "goals", "requirements", "acceptance"],
}
_WEIGHTS = {"coverage": 0.30, "structure": 0.20, "clarity": 0.20, "correctness": 0.20, "diagrams": 0.10}
_GATE_THRESHOLD = 70.0


def _score_coverage(text: str, scope: str) -> tuple[float, list[str]]:
    headings = {h.lower() for h in _HEADING_RX.findall(text)}
    required = _SCOPE_REQUIRED.get(scope, _SCOPE_REQUIRED["general"])
    missing = [r for r in required if not any(r in h for h in headings)]
    score = max(0.0, 100.0 - len(missing) * (100.0 / len(required)))
    fixes = [{"item": f"Add section: {m}", "dimension": "coverage", "priority": "high"} for m in missing]
    return score, fixes


def _score_structure(text: str) -> tuple[float, list[str]]:
    lines = text.splitlines()
    word_count = len(text.split())
    code_blocks = len(_CODE_FENCE_RX.findall(text)) // 2
    has_intro = bool(re.search(r"^#\s+", text, re.MULTILINE))
    score = 50.0
    fixes = []
    if word_count >= 200:
        score += 20.0
    else:
        fixes.append({"item": "Document is too short (< 200 words)", "dimension": "structure", "priority": "medium"})
    if has_intro:
        score += 15.0
    else:
        fixes.append({"item": "Add a top-level heading", "dimension": "structure", "priority": "high"})
    if code_blocks > 0:
        score += 15.0
    return min(100.0, score), fixes


def _score_clarity(text: str) -> tuple[float, list[str]]:
    broken = len(_BROKEN_LINK_RX.findall(text))
    score = max(0.0, 100.0 - broken * 20.0)
    fixes = [{"item": f"{broken} broken link(s) detected", "dimension": "clarity", "priority": "high"}] if broken else []
    return score, fixes


def _score_correctness(text: str) -> tuple[float, list[str]]:
    # Heuristic: count unmatched code fences
    fences = len(_CODE_FENCE_RX.findall(text))
    unmatched = fences % 2
    score = 100.0 if not unmatched else 60.0
    fixes = [{"item": "Unmatched code fence detected", "dimension": "correctness", "priority": "high"}] if unmatched else []
    return score, fixes


def _score_diagrams(text: str) -> tuple[float, list[str]]:
    has_diagram = bool(_DIAGRAM_RX.search(text)) or bool(_IMAGE_RX.search(text))
    score = 100.0 if has_diagram else 30.0
    fixes = [] if has_diagram else [{"item": "Add at least one diagram or image", "dimension": "diagrams", "priority": "low"}]
    return score, fixes


class PdfQualitySkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        manuscript_rel = kwargs.get("manuscript_path") or kwargs.get("document_path")
        if not manuscript_rel:
            return SkillResult(False, "pdf_quality", error="inputs.manuscript_path is required")

        manuscript_path = (repo_root / manuscript_rel).resolve() if not Path(manuscript_rel).is_absolute() else Path(manuscript_rel)
        if not manuscript_path.exists():
            return SkillResult(False, "pdf_quality", error=f"manuscript not found: {manuscript_path}")

        scope = str(kwargs.get("scope", "general")).lower()
        max_fixes = int(kwargs.get("max_fixes", 10))

        text = manuscript_path.read_text(encoding="utf-8", errors="ignore")

        dim_scores: dict[str, float] = {}
        all_fixes: list[dict] = []

        cov_score, cov_fixes = _score_coverage(text, scope)
        str_score, str_fixes = _score_structure(text)
        cla_score, cla_fixes = _score_clarity(text)
        cor_score, cor_fixes = _score_correctness(text)
        dia_score, dia_fixes = _score_diagrams(text)

        dim_scores = {
            "coverage": cov_score,
            "structure": str_score,
            "clarity": cla_score,
            "correctness": cor_score,
            "diagrams": dia_score,
        }
        all_fixes = (cov_fixes + str_fixes + cla_fixes + cor_fixes + dia_fixes)[:max_fixes]

        total = sum(_WEIGHTS[d] * dim_scores[d] for d in _WEIGHTS)
        gate_pass = total >= _GATE_THRESHOLD

        return SkillResult(
            True,
            "pdf_quality",
            data={
                "score": round(total, 1),
                "max_score": 100.0,
                "gate_pass": gate_pass,
                "gate_threshold": _GATE_THRESHOLD,
                "dimension_scores": {k: round(v, 1) for k, v in dim_scores.items()},
                "fix_list": all_fixes,
                "manuscript": str(manuscript_path),
            },
        )
