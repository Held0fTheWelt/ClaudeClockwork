#!/usr/bin/env python3
"""last_train

Summarize and optionally write out a last_train_report.json produced by
last_train_merge.  This is the *viewer/summarizer* counterpart to
last_train_merge (which is the *builder*).

Interface: run(req: dict) -> SkillResultSpec

Inputs:
  report_path     str   — path to an existing last_train_report.json
  output_format   str   — "json" | "markdown"  (default "json")
  write_summary   bool  — write output file to summary_dir  (default False)
  summary_dir     str   — directory for the written summary  (default ".report/")

Outputs:
  type                  "last_train_summary"
  timeline              [{step, verdict, notes}]
  combined_zip          str | null
  total_evolution_steps int
  total_loss_steps      int
  total_mixed_steps     int
  output_format         str
  status                "ok" | "error"
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _timeline_from_report(report: dict) -> list[dict]:
    raw = report.get("timeline") or []
    result = []
    for item in raw:
        verdict_obj = item.get("verdict") or {}
        classification = verdict_obj.get("classification", "unknown")
        confidence = verdict_obj.get("confidence", "low")
        reasons = verdict_obj.get("reasons") or []
        notes = f"confidence={confidence}; " + "; ".join(reasons) if reasons else f"confidence={confidence}"
        result.append({
            "step": item.get("index", len(result)),
            "verdict": classification,
            "notes": notes,
        })
    return result


def _count_by_verdict(timeline: list[dict], verdict: str) -> int:
    return sum(1 for t in timeline if t.get("verdict") == verdict)


def _build_markdown(timeline: list[dict], combined_zip: str | None, report: dict) -> str:
    lines = ["# Last-Train Summary", ""]
    if combined_zip:
        lines.append(f"**Combined zip:** `{combined_zip}`")
        lines.append("")

    total_evolution = _count_by_verdict(timeline, "evolution")
    total_loss = _count_by_verdict(timeline, "loss")
    total_mixed = _count_by_verdict(timeline, "mixed")

    lines.append(f"| Metric | Count |")
    lines.append(f"|---|---|")
    lines.append(f"| Evolution steps | {total_evolution} |")
    lines.append(f"| Loss steps | {total_loss} |")
    lines.append(f"| Mixed steps | {total_mixed} |")
    lines.append(f"| Total steps | {len(timeline)} |")
    lines.append("")

    if timeline:
        lines.append("## Timeline")
        lines.append("")
        lines.append("| Step | Verdict | Notes |")
        lines.append("|---|---|---|")
        for t in timeline:
            notes = t.get("notes", "").replace("|", "\\|")
            lines.append(f"| {t['step']} | **{t['verdict']}** | {notes} |")
        lines.append("")

    warnings = report.get("warnings") or []
    if warnings:
        lines.append("## Warnings")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    limitations = report.get("limitations") or []
    if limitations:
        lines.append("## Limitations")
        for lim in limitations:
            lines.append(f"- {lim}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}

    report_path_s = inputs.get("report_path", "")
    output_format = inputs.get("output_format", "json")
    write_summary = bool(inputs.get("write_summary", False))
    summary_dir_s = inputs.get("summary_dir", ".report/")

    # Validate report_path
    if not report_path_s:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "last_train",
            "status": "error",
            "outputs": {"type": "last_train_summary", "status": "error"},
            "errors": ["report_path is required"],
            "warnings": [],
            "metrics": {},
        }

    report_path = Path(report_path_s).expanduser()

    if not report_path.exists():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "last_train",
            "status": "error",
            "outputs": {"type": "last_train_summary", "status": "error"},
            "errors": [f"report_path not found: {report_path_s}"],
            "warnings": [],
            "metrics": {},
        }

    # Load report
    try:
        report = json.loads(report_path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "last_train",
            "status": "error",
            "outputs": {"type": "last_train_summary", "status": "error"},
            "errors": [f"Failed to parse report JSON: {exc}"],
            "warnings": [],
            "metrics": {},
        }

    # Build timeline
    timeline = _timeline_from_report(report)
    combined_zip = report.get("combined_zip_path") or report.get("combined_zip") or None

    total_evolution = _count_by_verdict(timeline, "evolution")
    total_loss = _count_by_verdict(timeline, "loss")
    total_mixed = _count_by_verdict(timeline, "mixed")

    summary_outputs: dict = {
        "type": "last_train_summary",
        "timeline": timeline,
        "combined_zip": combined_zip,
        "total_evolution_steps": total_evolution,
        "total_loss_steps": total_loss,
        "total_mixed_steps": total_mixed,
        "output_format": output_format,
        "status": "ok",
    }

    warnings: list[str] = []
    written_path: str | None = None

    if write_summary:
        import datetime
        date_tag = datetime.date.today().isoformat().replace("-", "")
        summary_dir = Path(summary_dir_s).expanduser()
        try:
            summary_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            warnings.append(f"Could not create summary_dir '{summary_dir_s}': {exc}")

        if output_format == "markdown":
            md_content = _build_markdown(timeline, combined_zip, report)
            out_file = summary_dir / f"last_train_summary_{date_tag}.md"
            try:
                out_file.write_text(md_content, encoding="utf-8")
                written_path = str(out_file)
            except Exception as exc:
                warnings.append(f"Failed to write markdown summary: {exc}")
        else:
            import datetime as dt
            payload = dict(summary_outputs)
            out_file = summary_dir / f"last_train_summary_{date_tag}.json"
            try:
                out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
                written_path = str(out_file)
            except Exception as exc:
                warnings.append(f"Failed to write JSON summary: {exc}")

    if written_path:
        summary_outputs["written_to"] = written_path

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "last_train",
        "status": "ok",
        "outputs": summary_outputs,
        "errors": [],
        "warnings": warnings,
        "metrics": {
            "timeline_steps": len(timeline),
            "evolution": total_evolution,
            "loss": total_loss,
            "mixed": total_mixed,
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
