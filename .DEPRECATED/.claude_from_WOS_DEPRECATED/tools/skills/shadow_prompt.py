#!/usr/bin/env python3
"""shadow_prompt

Triage a shadow_prompt_report.json produced by shadow_prompt_minify.
Classifies sections by quality score, ranks fixes, and optionally
writes a markdown triage file.

Interface: run(req: dict) -> SkillResultSpec

Inputs:
  report_path       str   — path to shadow_prompt_report.json
  min_quality_score float — accept threshold (default 0.6)
  write_triage      bool  — write triage file to triage_dir (default False)
  triage_dir        str   — directory for triage output (default ".report/")

Outputs:
  type                "shadow_prompt_triage"
  accept_sections     [str]
  flagged_sections    [str]
  rejected_sections   [str]
  ranked_fixes        [{section, current_score, suggested_action}]
  quality_gate_pass   bool
  status              "ok" | "error"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Classification thresholds
# ---------------------------------------------------------------------------

REJECT_THRESHOLD = 0.3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_sections(report: dict) -> list[dict]:
    """
    Extract section records from a shadow_prompt_report.
    The report may carry sections in several locations; we handle all known
    patterns gracefully and fall back to synthesising one section from the
    top-level quality_gap when no per-section data is found.
    """
    # Direct sections list (future schema extension)
    sections = report.get("sections") or []
    if sections:
        return list(sections)

    # written_files with per-file quality (another possible future field)
    outputs = report.get("outputs") or {}
    files_with_quality = outputs.get("files_with_quality") or []
    if files_with_quality:
        return list(files_with_quality)

    # Fall back: synthesise one section from quality_gap
    quality_gap = report.get("quality_gap") or {}
    score_raw = quality_gap.get("score_0_100", 0)
    # Normalise to 0-1 float
    score = float(score_raw) / 100.0 if score_raw > 1 else float(score_raw)

    written_files = outputs.get("written_files") or []
    if written_files:
        result = []
        per_file_score = score / max(len(written_files), 1)
        for f in written_files:
            result.append({"name": f, "content": "", "quality_score": per_file_score})
        return result

    # Absolute fallback: one synthetic section
    return [{"name": "shadow_prompt_report", "content": "", "quality_score": score}]


def _normalise_score(raw: object) -> float:
    """Accept int 0-100 or float 0-1, return float 0.0-1.0."""
    try:
        v = float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    if v > 1.0:
        v = v / 100.0
    return max(0.0, min(1.0, v))


def _suggested_action(score: float) -> str:
    if score < REJECT_THRESHOLD:
        return "remove"
    if score < 0.5:
        return "rewrite"
    return "expand"


def _write_triage_md(
    accept: list[dict],
    flagged: list[dict],
    rejected: list[dict],
    ranked_fixes: list[dict],
    quality_gate_pass: bool,
    min_quality_score: float,
) -> str:
    lines = ["# Shadow Prompt Triage Report", ""]
    gate_str = "PASS" if quality_gate_pass else "FAIL"
    lines.append(f"**Quality Gate:** {gate_str}")
    lines.append(f"**Min quality threshold:** {min_quality_score:.2f}")
    lines.append("")

    def _section_table(sections: list[dict], header: str) -> None:
        lines.append(f"## {header} ({len(sections)})")
        lines.append("")
        if not sections:
            lines.append("_None_")
            lines.append("")
            return
        lines.append("| Section | Score |")
        lines.append("|---|---|")
        for s in sections:
            name = s.get("name", "(unnamed)")
            score = _normalise_score(s.get("quality_score", 0))
            lines.append(f"| {name} | {score:.2f} |")
        lines.append("")

    _section_table(accept, "Accepted sections")
    _section_table(flagged, "Flagged sections")
    _section_table(rejected, "Rejected sections")

    if ranked_fixes:
        lines.append("## Ranked Fixes")
        lines.append("")
        lines.append("| # | Section | Score | Suggested Action |")
        lines.append("|---|---|---|---|")
        for i, fix in enumerate(ranked_fixes, 1):
            name = fix.get("section", "(unnamed)")
            score = fix.get("current_score", 0.0)
            action = fix.get("suggested_action", "")
            lines.append(f"| {i} | {name} | {score:.2f} | {action} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}

    report_path_s = inputs.get("report_path", "")
    min_quality_score = float(inputs.get("min_quality_score", 0.6))
    write_triage = bool(inputs.get("write_triage", False))
    triage_dir_s = inputs.get("triage_dir", ".report/")

    if not report_path_s:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "shadow_prompt",
            "status": "error",
            "outputs": {"type": "shadow_prompt_triage", "status": "error"},
            "errors": ["report_path is required"],
            "warnings": [],
            "metrics": {},
        }

    report_path = Path(report_path_s).expanduser()

    if not report_path.exists():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "shadow_prompt",
            "status": "error",
            "outputs": {"type": "shadow_prompt_triage", "status": "error"},
            "errors": [f"report_path not found: {report_path_s}"],
            "warnings": [],
            "metrics": {},
        }

    try:
        report = json.loads(report_path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "shadow_prompt",
            "status": "error",
            "outputs": {"type": "shadow_prompt_triage", "status": "error"},
            "errors": [f"Failed to parse report JSON: {exc}"],
            "warnings": [],
            "metrics": {},
        }

    # Extract and classify sections
    sections = _extract_sections(report)

    accept: list[dict] = []
    flagged: list[dict] = []
    rejected: list[dict] = []

    for s in sections:
        score = _normalise_score(s.get("quality_score", 0))
        if score >= min_quality_score:
            accept.append(s)
        elif score >= REJECT_THRESHOLD:
            flagged.append(s)
        else:
            rejected.append(s)

    # Build ranked_fixes from flagged + rejected, sorted ascending by score
    problem_sections = flagged + rejected
    ranked_fixes = sorted(
        [
            {
                "section": s.get("name", "(unnamed)"),
                "current_score": _normalise_score(s.get("quality_score", 0)),
                "suggested_action": _suggested_action(_normalise_score(s.get("quality_score", 0))),
            }
            for s in problem_sections
        ],
        key=lambda x: x["current_score"],
    )

    quality_gate_pass = len(rejected) == 0

    warnings: list[str] = []
    written_path: str | None = None

    if write_triage:
        import datetime
        date_tag = datetime.date.today().isoformat().replace("-", "")
        triage_dir = Path(triage_dir_s).expanduser()
        try:
            triage_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            warnings.append(f"Could not create triage_dir '{triage_dir_s}': {exc}")
        else:
            md = _write_triage_md(accept, flagged, rejected, ranked_fixes, quality_gate_pass, min_quality_score)
            out_file = triage_dir / f"shadow_prompt_triage_{date_tag}.md"
            try:
                out_file.write_text(md, encoding="utf-8")
                written_path = str(out_file)
            except Exception as exc:
                warnings.append(f"Failed to write triage file: {exc}")

    triage_outputs: dict = {
        "type": "shadow_prompt_triage",
        "accept_sections": [s.get("name", "(unnamed)") for s in accept],
        "flagged_sections": [s.get("name", "(unnamed)") for s in flagged],
        "rejected_sections": [s.get("name", "(unnamed)") for s in rejected],
        "ranked_fixes": ranked_fixes,
        "quality_gate_pass": quality_gate_pass,
        "status": "ok",
    }
    if written_path:
        triage_outputs["written_to"] = written_path

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "shadow_prompt",
        "status": "ok",
        "outputs": triage_outputs,
        "errors": [],
        "warnings": warnings,
        "metrics": {
            "sections_total": len(sections),
            "accepted": len(accept),
            "flagged": len(flagged),
            "rejected": len(rejected),
            "quality_gate_pass": quality_gate_pass,
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
