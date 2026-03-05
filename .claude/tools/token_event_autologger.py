#!/usr/bin/env python3
"""
token_event_autologger.py

A tiny wrapper to log a token event *automatically* after an agent action.

Usage patterns:
1) Env mode (recommended in automation):
   - set CLOCKWORK_RUN_ID, CLOCKWORK_ROLE, CLOCKWORK_MODEL, CLOCKWORK_TASK
   - set CLOCKWORK_PROMPT_TOKENS, CLOCKWORK_COMPLETION_TOKENS, CLOCKWORK_TOTAL_TOKENS (if available)
   - then call: python .claude/tools/token_event_autologger.py

2) JSON mode:
   python .claude/tools/token_event_autologger.py --json event.json

This tool does not call LLMs. It only logs.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import importlib.util
from pathlib import Path

# load event logger by file path
_mod_path = (Path(__file__).resolve().parent / "skills" / "_event_logger.py").resolve()
_spec = importlib.util.spec_from_file_location("_event_logger", _mod_path)
_elog = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_elog)  # type: ignore
now_iso = _elog.now_iso
resolve_events_file = _elog.resolve_events_file
append_event = _elog.append_event

def _safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="json_path", default=None)
    ap.add_argument("--events-file", dest="events_file", default=None)
    args = ap.parse_args()

    if args.json_path:
        event = json.loads(Path(args.json_path).read_text(encoding="utf-8", errors="ignore"))
    else:
        run_id = os.getenv("CLOCKWORK_RUN_ID", "run-unknown")
        role = os.getenv("CLOCKWORK_ROLE", "unknown")
        model = os.getenv("CLOCKWORK_MODEL", "unknown")
        task = os.getenv("CLOCKWORK_TASK", "unknown")
        phase = os.getenv("CLOCKWORK_PHASE", "")
        pt = _safe_int(os.getenv("CLOCKWORK_PROMPT_TOKENS", "0"))
        ct = _safe_int(os.getenv("CLOCKWORK_COMPLETION_TOKENS", "0"))
        tt = os.getenv("CLOCKWORK_TOTAL_TOKENS")
        total = _safe_int(tt, pt + ct)
        notes = os.getenv("CLOCKWORK_NOTES", "")
        event = {
            "ts": now_iso(),
            "run_id": run_id,
            "role": role,
            "model": model,
            "task": task,
            "phase": phase,
            "prompt_tokens": pt,
            "completion_tokens": ct,
            "total_tokens": total,
            "notes": notes,
        }

    run_id = str(event.get("run_id","run-unknown"))
    events_file = resolve_events_file(run_id, args.events_file or event.get("events_file"))
    append_event(event, events_file)
    print(f"[token_event_autologger] logged: run_id={run_id} role={event.get('role')} task={event.get('task')} tokens={event.get('total_tokens')} -> {events_file}")

if __name__ == "__main__":
    main()
