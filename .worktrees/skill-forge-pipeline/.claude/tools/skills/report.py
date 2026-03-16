#!/usr/bin/env python3
"""
report — MVP02 Markdown report builder skill.

Usage (standalone):
    python report.py '{"title": "My Report", "items": ["item one", "item two"]}'
    echo '{"title": "Test", "items": ["a", "b", "c"]}' | python report.py

Usage (via skill_runner):
    req["inputs"]["title"] — report heading (non-empty string)
    req["inputs"]["items"] — list of string items

Output (stdout JSON):
    {"report": "<markdown>", "item_count": N, "status": "ok"}
    {"report": "", "item_count": 0, "status": "fail", "error": "<reason>"}

Report format (Markdown):
    # <title>

    - <item 1>
    - <item 2>
    ...
"""

from __future__ import annotations
import json
import sys


def _build_report(title: str, items: list) -> dict:
    if not isinstance(title, str) or not title.strip():
        return {"report": "", "item_count": 0, "status": "fail",
                "error": "title must be a non-empty string"}
    if not isinstance(items, list):
        return {"report": "", "item_count": 0, "status": "fail",
                "error": "items must be a list of strings"}

    lines: list[str] = [f"# {title.strip()}", ""]
    valid_items: list[str] = []
    for item in items:
        if not isinstance(item, str):
            item = str(item)
        valid_items.append(item)
        lines.append(f"- {item}")
    lines.append("")  # trailing newline

    report_text = "\n".join(lines)
    return {"report": report_text, "item_count": len(valid_items), "status": "ok"}


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs") or req.get("input") or {}
    title = inputs.get("title", "")
    items = inputs.get("items", [])
    result = _build_report(title, items)
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "report",
        "status": result["status"],
        "outputs": result,
        "errors": [result["error"]] if result.get("error") else [],
        "warnings": [],
        "metrics": {"item_count": result.get("item_count", 0)},
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

    # Accept both bare input dict and wrapped SkillRequestSpec
    if data.get("type") == "skill_request_spec":
        result = run(data)
        sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        return 0 if result["status"] == "ok" else 1

    # Bare input: {"title": "...", "items": [...]}
    title = data.get("title", "")
    items = data.get("items", [])
    result = _build_report(title, items)
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
