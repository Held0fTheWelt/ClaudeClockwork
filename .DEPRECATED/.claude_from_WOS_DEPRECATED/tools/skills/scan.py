#!/usr/bin/env python3
"""
scan — MVP02 directory glob scanner skill.

Usage (standalone):
    python scan.py '{"path": ".", "pattern": "**/*.py"}'
    echo '{"path": ".claude/tools/skills", "pattern": "*.py"}' | python scan.py

Usage (via skill_runner):
    req["inputs"]["path"]    — root directory to search
    req["inputs"]["pattern"] — glob pattern (e.g. "**/*.py", "*.json")

Output (stdout JSON):
    {"files": [...], "count": N, "status": "ok"}
    {"files": [], "count": 0, "status": "fail", "error": "<reason>"}

Notes:
- Paths in the output are relative to the given search root.
- Uses pathlib.Path.glob (stdlib only, no external deps).
- Symlinks are not followed.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path


def _scan(path_str: str, pattern: str) -> dict:
    if not isinstance(path_str, str) or not path_str.strip():
        return {"files": [], "count": 0, "status": "fail",
                "error": "path must be a non-empty string"}
    if not isinstance(pattern, str) or not pattern.strip():
        return {"files": [], "count": 0, "status": "fail",
                "error": "pattern must be a non-empty string"}

    root = Path(path_str.strip())
    if not root.exists():
        return {"files": [], "count": 0, "status": "fail",
                "error": f"path does not exist: {path_str}"}
    if not root.is_dir():
        return {"files": [], "count": 0, "status": "fail",
                "error": f"path is not a directory: {path_str}"}

    try:
        matches = sorted(
            str(p.relative_to(root))
            for p in root.glob(pattern.strip())
            if p.is_file()
        )
    except Exception as exc:
        return {"files": [], "count": 0, "status": "fail",
                "error": f"glob error: {exc}"}

    return {"files": matches, "count": len(matches), "status": "ok"}


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs") or req.get("input") or {}
    path_str = inputs.get("path", "")
    pattern = inputs.get("pattern", "")
    result = _scan(path_str, pattern)
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "scan",
        "status": result["status"],
        "outputs": result,
        "errors": [result["error"]] if result.get("error") else [],
        "warnings": [],
        "metrics": {"file_count": result.get("count", 0)},
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

    # Bare input: {"path": "...", "pattern": "..."}
    path_str = data.get("path", "")
    pattern = data.get("pattern", "")
    result = _scan(path_str, pattern)
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
