#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from _event_logger import now_iso, resolve_events_file, append_event

DEFAULT_LIMITATIONS = [
    "This logs events only. It does not automatically read token counts from the platform.",
    "For true 'automatic' attribution, wrap each agent action to call this with observed token usage."
]

def _safe_int(x, default=0) -> int:
    try:
        return int(x)
    except Exception:
        return default

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    run_id = str(inputs.get("run_id","run-unknown"))
    role = str(inputs.get("role","unknown"))
    model = str(inputs.get("model","unknown"))
    task = str(inputs.get("task","unknown"))
    phase = str(inputs.get("phase",""))
    prompt_tokens = _safe_int(inputs.get("prompt_tokens", 0))
    completion_tokens = _safe_int(inputs.get("completion_tokens", 0))
    total_tokens = _safe_int(inputs.get("total_tokens", prompt_tokens + completion_tokens))
    notes = str(inputs.get("notes",""))
    ts = str(inputs.get("ts","")) or now_iso()

    events_file = resolve_events_file(run_id, inputs.get("events_file"))
    event = {
        "ts": ts,
        "run_id": run_id,
        "role": role,
        "model": model,
        "task": task,
        "phase": phase,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "notes": notes
    }
    append_event(event, events_file)

    cli = []
    cli.append("== Token Event Logged ==")
    cli.append(f"run_id: {run_id}")
    cli.append(f"role: {role} | model: {model} | task: {task} | tokens: {total_tokens}")
    cli.append(f"file: {events_file}")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"token_event_log",
        "status":"ok",
        "outputs":{
            "event": event,
            "events_file": str(events_file),
            "cli_summary": "\n".join(cli) + "\n"
        },
        "errors": [],
        "warnings": [],
        "metrics":{
            "total_tokens": total_tokens
        }
    }
