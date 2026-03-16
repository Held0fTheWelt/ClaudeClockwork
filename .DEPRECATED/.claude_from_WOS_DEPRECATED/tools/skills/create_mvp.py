#!/usr/bin/env python3
"""
create_mvp — CCW-MVP20: Autonomous MVP Generation skill.

Reads Clockwork_MVP_Chain.md, determines the next MVP number, generates a
new MVP entry following the exact chain format, and appends it atomically.
Logs the creation event to the audit log.

Usage (standalone):
    python3 create_mvp.py '{"skill_id":"create_mvp","inputs":{"trigger":"manual","mvp_name":"Test MVP","domain":"testing","scope":["test_skill"],"dry_run":true}}'

Usage (via skill_runner):
    The run(req) interface is called with a SkillRequestSpec dict.

Output (stdout JSON, SkillResultSpec):
    {"type": "skill_result_spec", "skill_id": "create_mvp", "status": "ok"|"dry_run"|"error", ...}
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[3]  # .claude/tools/skills/ -> repo root
_CHAIN_FILE = _REPO_ROOT / ".claude-development" / "Clockwork_MVP_Chain.md"
_AUDIT_LOG_DIR = _REPO_ROOT / ".claude-development" / "audits" / "logs"


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _find_last_mvp_number(chain_text: str) -> int:
    """Return the highest CCW-MVPNN number found in the chain file."""
    matches = re.findall(r"#\s*CCW-MVP(\d+)", chain_text)
    if not matches:
        return 0
    return max(int(m) for m in matches)


def _infer_mvp_name(trigger: str, trigger_ref: str | None, domain: str, scope: list) -> str:
    """Produce a reasonable MVP name when the caller does not supply one."""
    if trigger == "audit_gap" and trigger_ref:
        ref_stem = Path(trigger_ref).stem
        return f"Gap Closure — {ref_stem}"
    if trigger == "defect" and trigger_ref:
        ref_stem = Path(trigger_ref).stem
        return f"Defect Fix — {ref_stem}"
    if trigger == "parity_scan":
        return f"Parity Follow-up — {domain.title()}"
    if scope:
        return f"{domain.title()} — {', '.join(scope[:2])}"
    return f"{domain.title()} Enhancement"


def _build_mvp_entry(mvp_id: str, mvp_name: str, domain: str, scope: list,
                     trigger: str, trigger_ref: str | None) -> str:
    """Render the MVP markdown block following the chain format."""
    scope_list = "\n".join(f"  - `{s}`" for s in scope) if scope else "  - (none specified)"
    trigger_note = ""
    if trigger_ref:
        trigger_note = f"\nTriggered by: `{trigger_ref}`"
    lines = [
        f"# {mvp_id} — {mvp_name}",
        f"**Goal:** Implement capabilities in the **{domain}** domain as identified by "
        f"trigger `{trigger}`.{trigger_note}",
        "",
        "## Deliverables",
        "",
        "- Scope (skill IDs / capability gaps addressed):",
        scope_list,
        "- Schema, example, and Python implementation for each new skill",
        "- Registry entries added to `skills/registry.md`",
        "- `SKILLS` dispatch entries added to `skill_runner.py`",
        "",
        "## Acceptance",
        "- All skills listed in scope run end-to-end via skill_runner",
        "- Each skill has schema + example + .py",
        "- Smoke test for each skill returns `status: ok` or `status: error` with clear message",
    ]
    return "\n".join(lines)


def _append_to_chain(chain_path: Path, entry_text: str) -> None:
    """Atomically append the MVP entry to the chain file."""
    current = chain_path.read_text(encoding="utf-8")
    # Strip trailing whitespace/newlines from existing content
    updated = current.rstrip() + "\n\n---\n\n" + entry_text + "\n"
    tmp = chain_path.with_suffix(".md.tmp")
    tmp.write_text(updated, encoding="utf-8")
    tmp.replace(chain_path)


def _append_audit_log(mvp_id: str, mvp_name: str, trigger: str,
                      trigger_ref: str | None, dry_run: bool) -> None:
    """Append a one-line entry to today's audit log."""
    _AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    log_file = _AUDIT_LOG_DIR / f"audit_log_{today}.md"
    dry_tag = " [dry_run]" if dry_run else ""
    entry = (
        f"\n## {today} — {mvp_id} created{dry_tag}\n"
        f"- **MVP:** {mvp_id} — {mvp_name}\n"
        f"- **Trigger:** `{trigger}`"
        + (f"\n- **Trigger ref:** `{trigger_ref}`" if trigger_ref else "")
        + f"\n- **Skill:** create_mvp (CCW-MVP20)\n"
    )
    with log_file.open("a", encoding="utf-8") as f:
        f.write(entry)


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def _execute(inputs: dict) -> dict:
    trigger = inputs.get("trigger", "manual")
    trigger_ref = inputs.get("trigger_ref") or None
    mvp_name_in = inputs.get("mvp_name") or None
    domain = inputs.get("domain") or "general"
    scope = inputs.get("scope") or []
    dry_run = bool(inputs.get("dry_run", False))

    # Validate trigger
    valid_triggers = {"user_instruction", "audit_gap", "defect", "parity_scan", "manual"}
    if trigger not in valid_triggers:
        return {
            "mvp_id": None,
            "mvp_entry": None,
            "written_to": None,
            "status": "error",
            "error": f"trigger must be one of {sorted(valid_triggers)}, got: {trigger!r}",
        }

    # Read chain file
    if not _CHAIN_FILE.exists():
        return {
            "mvp_id": None,
            "mvp_entry": None,
            "written_to": None,
            "status": "error",
            "error": f"Chain file not found: {_CHAIN_FILE}",
        }

    chain_text = _CHAIN_FILE.read_text(encoding="utf-8")
    last_num = _find_last_mvp_number(chain_text)
    next_num = last_num + 1
    mvp_id = f"CCW-MVP{next_num:02d}"

    # Resolve MVP name
    mvp_name = mvp_name_in or _infer_mvp_name(trigger, trigger_ref, domain, scope)

    # Build entry
    entry = _build_mvp_entry(mvp_id, mvp_name, domain, scope, trigger, trigger_ref)

    if dry_run:
        _append_audit_log(mvp_id, mvp_name, trigger, trigger_ref, dry_run=True)
        return {
            "mvp_id": mvp_id,
            "mvp_entry": entry,
            "written_to": None,
            "status": "dry_run",
        }

    # Append to chain
    _append_to_chain(_CHAIN_FILE, entry)
    _append_audit_log(mvp_id, mvp_name, trigger, trigger_ref, dry_run=False)

    return {
        "mvp_id": mvp_id,
        "mvp_entry": entry,
        "written_to": str(_CHAIN_FILE),
        "status": "ok",
    }


def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs") or req.get("input") or {}
    try:
        result = _execute(inputs)
    except Exception as exc:
        result = {
            "mvp_id": None,
            "mvp_entry": None,
            "written_to": None,
            "status": "error",
            "error": str(exc),
        }
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "create_mvp",
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

    if data.get("type") == "skill_request_spec" or "skill_id" in data:
        result = run(data)
    else:
        # Bare inputs dict
        result = run({"inputs": data})

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["status"] in ("ok", "dry_run") else 1


if __name__ == "__main__":
    raise SystemExit(main())
