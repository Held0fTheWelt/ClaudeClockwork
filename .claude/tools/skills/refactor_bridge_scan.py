#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

DEFAULT_MARKERS = ["src", "oodle", ".oodle", "claude-documents", "Docs/Rules"]


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    project_root = Path(inputs.get("project_root", ".")).resolve()
    markers = inputs.get("markers", DEFAULT_MARKERS)
    if isinstance(markers, str):
        markers = [markers]

    found = []
    for m in markers:
        p = project_root / m
        if p.exists():
            found.append({"marker": m, "path": str(p)})

    suggestions = []
    for f in found:
        m = f["marker"]
        if m == "src":
            suggestions.append("If packaging does not use src-layout, archive src/ under quellen/legacy/src_prototype/")
        if m in {"oodle", ".oodle"}:
            suggestions.append("Consider migrating runtime/package naming away from 'oodle' to avoid relic namespace")
        if m == "claude-documents":
            suggestions.append("Move canonical fixtures/schemas to quellen/ and update tests to reference that")
        if m == "Docs/Rules":
            suggestions.append("Docs/Rules is deprecated by .claude/ - archive or delete to avoid drift")

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "refactor_bridge_scan"),
        "status": "ok",
        "outputs": {"project_root": str(project_root), "found": found, "suggestions": suggestions},
        "metrics": {"found": len(found), "suggestions": len(suggestions)},
        "errors": [],
        "warnings": [],
    }
