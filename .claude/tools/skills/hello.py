#!/usr/bin/env python3
"""
hello — MVP02 greeting skill.

Usage (standalone):
    python hello.py '{"name": "World"}'
    echo '{"name": "Alice"}' | python hello.py

Usage (via skill_runner):
    The run(req) interface is called with a SkillRequestSpec dict.
    req["inputs"]["name"] must be a non-empty string.

Output (stdout JSON):
    {"message": "Hello, <name>!", "status": "ok"}
    {"message": "", "status": "fail", "error": "<reason>"}
"""

from __future__ import annotations
import json
import sys


def _greet(name: str) -> dict:
    if not isinstance(name, str) or not name.strip():
        return {"message": "", "status": "fail", "error": "name must be a non-empty string"}
    return {"message": f"Hello, {name.strip()}!", "status": "ok"}


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs") or req.get("input") or {}
    name = inputs.get("name", "")
    result = _greet(name)
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "hello",
        "status": result["status"],
        "outputs": result,
        "errors": [result["error"]] if result.get("error") else [],
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
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON input: {exc}\n")
        return 1

    # Accept both bare input dict and wrapped SkillRequestSpec
    if data.get("type") == "skill_request_spec":
        result = run(data)
        sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        return 0 if result["status"] == "ok" else 1

    # Bare input: {"name": "..."}
    name = data.get("name", "")
    result = _greet(name)
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
