#!/usr/bin/env python3
"""pdf_quality

Deterministic quality rubric scorer for Markdown manuscripts.
No LLM calls — all scoring is based on measurable document properties.

Interface: run(req: dict) -> SkillResultSpec

Inputs:
  manuscript_path  str   — path to Markdown file to evaluate
  scope            str   — "lastenheft" | "tutorial" | "api_docs" | "general"  (default "general")
  target_audience  str   — "developer" | "enduser" | "manager"  (default "developer")
  max_fixes        int   — max fix items in output  (default 10)
  write_report     bool  — write report file  (default False)
  report_dir       str   — directory for report output  (default ".report/")

Outputs:
  type             "quality_gap_report"
  score            float  (0-100, weighted average)
  dimension_scores {coverage, structure, clarity, correctness, diagrams}
  fix_list         [{item, dimension, priority}]
  gate_pass        bool  (score >= 70)
  status           "ok" | "error"
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from statistics import mean

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GATE_THRESHOLD = 70.0
CODE_FENCE_RX = re.compile(r"```")
BROKEN_LINK_RX = re.compile(r"\[([^\]]+)\]\(\s*\)")
DIAGRAM_BLOCK_RX = re.compile(r"```\s*(mermaid|diagram|plantuml|graphviz)", re.IGNORECASE)
IMAGE_RX = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

# Scope → required ## headings (lower-cased keywords)
SCOPE_REQUIRED_SECTIONS: dict[str, list[str]] = {
    "general": ["introduction", "usage", "examples", "reference"],
    "lastenheft": ["einleitung", "ziele", "anforderungen", "abnahmekriterien"],
    "tutorial": ["introduction", "prerequisites", "steps", "summary"],
    "api_docs": ["overview", "authentication", "endpoints", "examples"],
}

WEIGHTS = {
    "coverage": 0.30,
    "structure": 0.20,
    "clarity": 0.20,
    "correctness": 0.20,
    "diagrams": 0.10,
}


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def _score_coverage(lines: list[str], scope: str) -> float:
    """Count of required ## headings found / expected minimum, capped at 100."""
    required = SCOPE_REQUIRED_SECTIONS.get(scope, SCOPE_REQUIRED_SECTIONS["general"])
    text_lower = "\n".join(lines).lower()
    found = sum(1 for kw in required if kw in text_lower)
    if not required:
        return 100.0
    return min(100.0, (found / len(required)) * 100.0)


def _score_structure(lines: list[str]) -> float:
    """
    Ratio of heading lines to total non-empty lines.
    Penalty if fewer than 1 heading per 20 non-empty lines.
    """
    non_empty = [l for l in lines if l.strip()]
    total = len(non_empty)
    if total == 0:
        return 0.0
    headings = [l for l in non_empty if l.strip().startswith("#")]
    heading_count = len(headings)
    if heading_count == 0:
        return 0.0
    ratio = heading_count / total
    # Ideal: at least 1 heading per 20 lines = ratio >= 0.05
    # Score proportionally, max 100
    score = min(100.0, ratio * 2000.0)  # 0.05 → 100
    return score


def _score_clarity(lines: list[str]) -> float:
    """
    Avg sentence length (words) in non-code paragraphs.
    Target: < 25 words per sentence.
    Score 100 if avg <= 15, decreasing toward 0 at >= 40 words.
    """
    in_code = False
    sentences: list[int] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or stripped.startswith("#") or stripped.startswith("|"):
            continue
        # Split on sentence terminators
        for sent in re.split(r"[.!?]+", stripped):
            words = sent.split()
            if len(words) >= 3:
                sentences.append(len(words))

    if not sentences:
        return 80.0  # neutral if no prose found

    avg = mean(sentences)
    if avg <= 15:
        return 100.0
    if avg >= 40:
        return 0.0
    # Linear interpolation: 15→100, 40→0
    return max(0.0, 100.0 - (avg - 15.0) * (100.0 / 25.0))


def _score_correctness(lines: list[str], text: str) -> float:
    """
    Penalise:
    - broken markdown links  ([text]( without valid URL)
    - unclosed code fences   (odd number of ``` markers)
    Each issue subtracts 20 points from 100.
    """
    score = 100.0
    broken_links = BROKEN_LINK_RX.findall(text)
    score -= len(broken_links) * 20.0

    fence_count = len(CODE_FENCE_RX.findall(text))
    if fence_count % 2 != 0:
        score -= 20.0

    return max(0.0, score)


def _score_diagrams(text: str) -> float:
    """
    Returns 100 if at least one mermaid/diagram block or image reference found,
    50 if only image refs, 0 otherwise.
    """
    if DIAGRAM_BLOCK_RX.search(text):
        return 100.0
    if IMAGE_RX.search(text):
        return 50.0
    return 0.0


def _overall(dim: dict[str, float]) -> float:
    return sum(dim[k] * WEIGHTS[k] for k in WEIGHTS)


def _priority(score: float) -> str:
    if score < 40:
        return "high"
    if score < 70:
        return "medium"
    return "low"


def _build_fix_list(dim_scores: dict[str, float], max_fixes: int) -> list[dict]:
    suggestions: dict[str, str] = {
        "coverage": "Add missing required sections (## headings) for the chosen scope.",
        "structure": "Add more headings; target at least 1 heading per 20 lines of prose.",
        "clarity": "Shorten sentences to under 25 words; prefer active voice.",
        "correctness": "Fix broken markdown links and close all open code fences.",
        "diagrams": "Add at least one Mermaid diagram block or image reference.",
    }
    fixes = []
    for dim, score in sorted(dim_scores.items(), key=lambda x: x[1]):
        if score < GATE_THRESHOLD and len(fixes) < max_fixes:
            fixes.append({
                "item": suggestions.get(dim, f"Improve {dim}."),
                "dimension": dim,
                "priority": _priority(score),
            })
    return fixes


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def _write_report_md(
    manuscript_path: str,
    scope: str,
    target_audience: str,
    overall: float,
    dim: dict[str, float],
    fixes: list[dict],
    gate_pass: bool,
) -> str:
    lines = [
        "# PDF Quality Report",
        "",
        f"**Manuscript:** `{manuscript_path}`",
        f"**Scope:** {scope}  **Audience:** {target_audience}",
        f"**Overall score:** {overall:.1f} / 100",
        f"**Gate:** {'PASS' if gate_pass else 'FAIL'} (threshold {GATE_THRESHOLD})",
        "",
        "## Dimension Scores",
        "",
        "| Dimension | Score | Weight |",
        "|---|---|---|",
    ]
    for dim_name, w in WEIGHTS.items():
        lines.append(f"| {dim_name} | {dim[dim_name]:.1f} | {int(w*100)}% |")
    lines.append("")

    if fixes:
        lines.append("## Fix List")
        lines.append("")
        lines.append("| # | Priority | Dimension | Suggestion |")
        lines.append("|---|---|---|---|")
        for i, fix in enumerate(fixes, 1):
            lines.append(f"| {i} | {fix['priority']} | {fix['dimension']} | {fix['item']} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}

    manuscript_path_s = inputs.get("manuscript_path", "")
    scope = inputs.get("scope", "general")
    target_audience = inputs.get("target_audience", "developer")
    max_fixes = int(inputs.get("max_fixes", 10))
    write_report = bool(inputs.get("write_report", False))
    report_dir_s = inputs.get("report_dir", ".report/")

    if not manuscript_path_s:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "pdf_quality",
            "status": "error",
            "outputs": {"type": "quality_gap_report", "status": "error"},
            "errors": ["manuscript_path is required"],
            "warnings": [],
            "metrics": {},
        }

    manuscript_path = Path(manuscript_path_s).expanduser()

    if not manuscript_path.exists():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "pdf_quality",
            "status": "error",
            "outputs": {"type": "quality_gap_report", "status": "error"},
            "errors": [f"manuscript_path not found: {manuscript_path_s}"],
            "warnings": [],
            "metrics": {},
        }

    try:
        text = manuscript_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "pdf_quality",
            "status": "error",
            "outputs": {"type": "quality_gap_report", "status": "error"},
            "errors": [f"Failed to read manuscript: {exc}"],
            "warnings": [],
            "metrics": {},
        }

    lines = text.splitlines()

    # Normalise scope
    if scope not in SCOPE_REQUIRED_SECTIONS:
        scope = "general"

    dim_scores = {
        "coverage": _score_coverage(lines, scope),
        "structure": _score_structure(lines),
        "clarity": _score_clarity(lines),
        "correctness": _score_correctness(lines, text),
        "diagrams": _score_diagrams(text),
    }

    overall = _overall(dim_scores)
    gate_pass = overall >= GATE_THRESHOLD
    fix_list = _build_fix_list(dim_scores, max_fixes)

    warnings: list[str] = []
    written_path: str | None = None

    if write_report:
        import datetime
        date_tag = datetime.date.today().isoformat().replace("-", "")
        report_dir = Path(report_dir_s).expanduser()
        try:
            report_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            warnings.append(f"Could not create report_dir '{report_dir_s}': {exc}")
        else:
            md = _write_report_md(
                manuscript_path_s, scope, target_audience,
                overall, dim_scores, fix_list, gate_pass,
            )
            stem = manuscript_path.stem
            out_file = report_dir / f"pdf_quality_{stem}_{date_tag}.md"
            try:
                out_file.write_text(md, encoding="utf-8")
                written_path = str(out_file)
            except Exception as exc:
                warnings.append(f"Failed to write report: {exc}")

    quality_outputs: dict = {
        "type": "quality_gap_report",
        "score": round(overall, 2),
        "dimension_scores": {k: round(v, 2) for k, v in dim_scores.items()},
        "fix_list": fix_list,
        "gate_pass": gate_pass,
        "status": "ok",
    }
    if written_path:
        quality_outputs["written_to"] = written_path

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "pdf_quality",
        "status": "ok",
        "outputs": quality_outputs,
        "errors": [],
        "warnings": warnings,
        "metrics": {
            "overall_score": round(overall, 2),
            "gate_pass": gate_pass,
            "fix_count": len(fix_list),
        },
    }


# ---------------------------------------------------------------------------
# Standalone entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) >= 2:
        raw = sys.argv[1]
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON input: {exc}\n")
        return 1

    if data.get("type") == "skill_request_spec" or "inputs" in data:
        result = run(data)
    else:
        result = run({"inputs": data})

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
