#!/usr/bin/env python3
"""
parity_scan_and_mvp_planner — CCW-MVP16 Parity Audit Skill.

Deterministic file-evidence parity scanner. Reads the MVP chain, scans the
repo for file evidence, classifies each capability as FULL/PARTIAL/GAP, writes
a parity matrix + missing features backlog, and optionally writes an MVP pre-plan.

No LLM calls — purely file I/O (stdlib only).

Usage (via skill_runner):
    Skill ID: parity_scan_and_mvp_planner

Usage (standalone):
    python parity_scan_and_mvp_planner.py '{"skill_id":"parity_scan_and_mvp_planner","inputs":{"run_date":"2026-03-02"}}'

Schema: contracts/schemas/parity_scan_and_mvp_planner.schema.json
Example: contracts/examples/parity_scan_and_mvp_planner_example.json
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SKILL_ID = "parity_scan_and_mvp_planner"

# Patterns that indicate a deliverable file reference in an MVP section.
# We look for backtick-wrapped paths or bullet points naming files.
_FILE_REF_RE = re.compile(r"`([^`]+\.[a-zA-Z0-9_]+)`")

# Heading pattern that marks an MVP section (## CCW-MVP## or ## MVP##)
_MVP_HEADING_RE = re.compile(
    r"^#{1,3}\s+(CCW-MVP\d+|MVP\d+)\s*[—–-]?\s*(.*)", re.IGNORECASE
)


def _extract_mvp_sections(chain_text: str) -> list[dict]:
    """
    Parse the MVP chain markdown into a list of:
      {"mvp_id": str, "title": str, "deliverables": [str]}

    Deliverables are file-path tokens found inside backticks.
    """
    sections: list[dict] = []
    current: dict | None = None

    for line in chain_text.splitlines():
        m = _MVP_HEADING_RE.match(line)
        if m:
            if current is not None:
                sections.append(current)
            current = {
                "mvp_id": m.group(1).upper(),
                "title": m.group(2).strip(),
                "deliverables": [],
                "raw_lines": [],
            }
        elif current is not None:
            current["raw_lines"].append(line)
            for ref in _FILE_REF_RE.findall(line):
                # Filter to items that look like file paths (contain / or .)
                if "/" in ref or ("." in ref and not ref.startswith(".")):
                    current["deliverables"].append(ref)

    if current is not None:
        sections.append(current)

    return sections


def _file_exists(root: Path, rel_path: str) -> bool:
    """Check whether a relative path exists under root."""
    target = root / rel_path
    return target.exists()


def _classify_section(root: Path, deliverables: list[str]) -> tuple[str, list[str], list[str]]:
    """
    Returns (status, found_files, missing_files).
    status is FULL | PARTIAL | GAP.
    """
    if not deliverables:
        # No declared deliverables — treat as GAP (undeclared)
        return "GAP", [], []

    found: list[str] = []
    missing: list[str] = []

    for d in deliverables:
        if _file_exists(root, d):
            found.append(d)
        else:
            missing.append(d)

    if missing and not found:
        return "GAP", found, missing
    elif missing:
        return "PARTIAL", found, missing
    else:
        return "FULL", found, missing


def _status_emoji(status: str) -> str:
    return {"FULL": "FULL", "PARTIAL": "PARTIAL", "GAP": "GAP"}.get(status, status)


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def _write_parity_matrix(
    output_path: Path,
    rows: list[dict],
    run_date: str,
) -> None:
    lines = [
        f"# Parity Matrix — {run_date}",
        "",
        f"_Generated: {run_date} by {_SKILL_ID}_",
        "",
        "| MVP | Title | Status | Evidence (found) | Gaps (missing) |",
        "|-----|-------|--------|-----------------|----------------|",
    ]
    for row in rows:
        mvp_id = row["mvp_id"]
        title = row["title"]
        status = row["status"]
        found = ", ".join(f"`{f}`" for f in row["found"]) or "—"
        missing = ", ".join(f"`{m}`" for m in row["missing"]) or "—"
        lines.append(f"| {mvp_id} | {title} | {status} | {found} | {missing} |")

    lines += [
        "",
        "## Summary",
        "",
        f"- FULL: {sum(1 for r in rows if r['status'] == 'FULL')}",
        f"- PARTIAL: {sum(1 for r in rows if r['status'] == 'PARTIAL')}",
        f"- GAP: {sum(1 for r in rows if r['status'] == 'GAP')}",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_backlog(
    output_path: Path,
    gap_rows: list[dict],
    partial_rows: list[dict],
    run_date: str,
) -> None:
    lines = [
        f"# Missing Features Backlog — {run_date}",
        "",
        f"_Generated: {run_date} by {_SKILL_ID}_",
        "",
        "Items are listed in MVP order. Priorities are not assigned in this implementation.",
        "",
    ]

    if gap_rows:
        lines += ["## GAP Items (no evidence found)", ""]
        for row in gap_rows:
            missing_str = ", ".join(f"`{m}`" for m in row["missing"]) if row["missing"] else "no deliverables declared"
            lines.append(f"- **{row['mvp_id']}** ({row['title']}): {missing_str}")
        lines.append("")

    if partial_rows:
        lines += ["## PARTIAL Items (some evidence missing)", ""]
        for row in partial_rows:
            missing_str = ", ".join(f"`{m}`" for m in row["missing"])
            lines.append(f"- **{row['mvp_id']}** ({row['title']}): missing {missing_str}")
        lines.append("")

    if not gap_rows and not partial_rows:
        lines.append("_No gaps or partial items found._")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_mvp_plan(
    output_path: Path,
    gap_rows: list[dict],
    partial_rows: list[dict],
    run_date: str,
) -> None:
    lines = [
        f"# M2 Parity Follow-up Plan — {run_date}",
        "",
        f"_Generated: {run_date} by {_SKILL_ID}_",
        "",
        "## Objective",
        "",
        "Address all GAP and PARTIAL items identified in the parity scan.",
        "",
        "## Action Items",
        "",
    ]

    priority = 1
    for row in gap_rows:
        missing_str = ", ".join(f"`{m}`" for m in row["missing"]) if row["missing"] else "undeclared deliverables"
        lines.append(f"{priority}. **{row['mvp_id']}** — Implement missing deliverables: {missing_str}")
        priority += 1

    for row in partial_rows:
        missing_str = ", ".join(f"`{m}`" for m in row["missing"])
        lines.append(f"{priority}. **{row['mvp_id']}** — Complete partial deliverables: {missing_str}")
        priority += 1

    if priority == 1:
        lines.append("_No action items — all MVPs are at FULL parity._")

    lines += [
        "",
        "## Next Steps",
        "",
        "1. Prioritize GAP items by impact (P0/P1/P2) in subsequent planning.",
        "2. Re-run `parity_scan_and_mvp_planner` after each MVP delivery.",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main skill logic
# ---------------------------------------------------------------------------

def _run_scan(req: dict) -> dict:
    inputs = req.get("inputs") or {}
    run_date: str = inputs.get("run_date") or datetime.now().strftime("%Y-%m-%d")
    reference_mvp_chain: str = inputs.get(
        "reference_mvp_chain", ".claude-development/Clockwork_MVP_Chain.md"
    )
    output_dir_str: str = inputs.get("output_dir", ".claude-development/audits/parity/")
    generate_mvp_plan: bool = bool(inputs.get("generate_mvp_plan", False))
    mvp_plan_output_dir_str: str = inputs.get(
        "mvp_plan_output_dir", ".claude-development/milestones/"
    )

    errors: list[str] = []

    # Resolve repo root — walk up from cwd until we find .claude/
    repo_root = Path.cwd()
    for candidate in [repo_root] + list(repo_root.parents):
        if (candidate / ".claude").exists():
            repo_root = candidate
            break

    # Read MVP chain
    chain_path = repo_root / reference_mvp_chain
    if not chain_path.exists():
        errors.append(f"MVP chain file not found: {chain_path}")
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": _SKILL_ID,
            "status": "error",
            "outputs": {
                "parity_matrix": None,
                "backlog": None,
                "mvp_plan": None,
                "gap_count": 0,
                "partial_count": 0,
                "full_count": 0,
                "p0_count": 0,
                "p1_count": 0,
                "p2_count": 0,
                "status": "error",
                "errors": errors,
            },
            "errors": errors,
            "warnings": [],
            "metrics": {},
        }

    chain_text = chain_path.read_text(encoding="utf-8", errors="replace")

    # Parse MVP sections
    sections = _extract_mvp_sections(chain_text)

    # Classify each section
    rows: list[dict] = []
    for sec in sections:
        status, found, missing = _classify_section(repo_root, sec["deliverables"])
        rows.append(
            {
                "mvp_id": sec["mvp_id"],
                "title": sec["title"],
                "status": status,
                "found": found,
                "missing": missing,
            }
        )

    gap_rows = [r for r in rows if r["status"] == "GAP"]
    partial_rows = [r for r in rows if r["status"] == "PARTIAL"]
    full_rows = [r for r in rows if r["status"] == "FULL"]

    gap_count = len(gap_rows)
    partial_count = len(partial_rows)
    full_count = len(full_rows)

    # Ensure output directories exist
    output_dir = repo_root / output_dir_str
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write parity matrix
    matrix_path = output_dir / f"parity_matrix_{run_date}.md"
    try:
        _write_parity_matrix(matrix_path, rows, run_date)
    except Exception as exc:
        errors.append(f"Failed to write parity matrix: {exc}")

    # Write backlog
    backlog_path = output_dir / f"missing_features_backlog_{run_date}.md"
    try:
        _write_backlog(backlog_path, gap_rows, partial_rows, run_date)
    except Exception as exc:
        errors.append(f"Failed to write backlog: {exc}")

    # Optionally write MVP plan
    mvp_plan_path: Path | None = None
    if generate_mvp_plan:
        mvp_plan_dir = repo_root / mvp_plan_output_dir_str
        mvp_plan_dir.mkdir(parents=True, exist_ok=True)
        mvp_plan_path = mvp_plan_dir / f"M2_parity_followup_plan_{run_date}.md"
        try:
            _write_mvp_plan(mvp_plan_path, gap_rows, partial_rows, run_date)
        except Exception as exc:
            errors.append(f"Failed to write MVP plan: {exc}")
            mvp_plan_path = None

    status_out = "error" if errors and not matrix_path.exists() else "ok"
    if errors and matrix_path.exists():
        status_out = "ok"  # partial success but main outputs written

    outputs = {
        "parity_matrix": str(matrix_path.resolve()) if matrix_path.exists() else None,
        "backlog": str(backlog_path.resolve()) if backlog_path.exists() else None,
        "mvp_plan": str(mvp_plan_path.resolve()) if mvp_plan_path and mvp_plan_path.exists() else None,
        "gap_count": gap_count,
        "partial_count": partial_count,
        "full_count": full_count,
        "p0_count": 0,
        "p1_count": 0,
        "p2_count": 0,
        "status": status_out,
        "errors": errors,
    }

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": _SKILL_ID,
        "status": status_out,
        "outputs": outputs,
        "errors": errors,
        "warnings": [],
        "metrics": {
            "mvps_scanned": len(rows),
            "gap_count": gap_count,
            "partial_count": partial_count,
            "full_count": full_count,
        },
    }


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    try:
        return _run_scan(req)
    except Exception as exc:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": _SKILL_ID,
            "status": "error",
            "outputs": {
                "parity_matrix": None,
                "backlog": None,
                "mvp_plan": None,
                "gap_count": 0,
                "partial_count": 0,
                "full_count": 0,
                "p0_count": 0,
                "p1_count": 0,
                "p2_count": 0,
                "status": "error",
                "errors": [str(exc)],
            },
            "errors": [str(exc)],
            "warnings": [],
            "metrics": {},
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
        req = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON input: {exc}\n")
        return 1

    result = run(req)
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
