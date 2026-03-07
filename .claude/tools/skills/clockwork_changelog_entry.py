#!/usr/bin/env python3
"""
clockwork_changelog_entry — Generate or update changelog entry for current version.

Usage (via skill_runner):
    python3 .claude/tools/skills/skill_runner.py '{"skill_id":"clockwork_changelog_entry","inputs":{}}'

Output (stdout JSON):
    {"status": "ok", "entry": "<changelog_entry>"}
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime


def _read_version() -> str:
    """Read current version from .claude/VERSION."""
    try:
        version_file = Path(".").resolve() / ".claude" / "VERSION"
        if not version_file.exists():
            version_file = Path(".").resolve() / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return "0.0.0"


def _generate_changelog_entry(version: str, date: str | None = None) -> str:
    """Generate a changelog entry for the given version."""
    if date is None:
        date = datetime.utcnow().strftime("%Y-%m-%d")
    return f"## [{version}] — {date}\n\nNo changes recorded yet.\n"


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs") or {}

    version = inputs.get("version") or _read_version()
    date = inputs.get("date") or datetime.utcnow().strftime("%Y-%m-%d")

    entry = _generate_changelog_entry(version, date)

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "clockwork_changelog_entry",
        "status": "ok",
        "outputs": {
            "version": version,
            "date": date,
            "entry": entry,
        },
        "errors": [],
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
        print(json.dumps({"error": f"invalid JSON: {exc}"}))
        return 2

    result = run(req)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
