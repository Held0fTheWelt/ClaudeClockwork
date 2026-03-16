#!/usr/bin/env python3
from __future__ import annotations
import json, datetime
from collections import defaultdict
from pathlib import Path

def _read_jsonl(p: Path) -> list[dict]:
    events=[]
    if not p.exists():
        return events
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    return events

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    ledger_path = Path(inputs.get("ledger",".clockwork_runtime/knowledge/outcome_ledger.jsonl"))
    events = _read_jsonl(ledger_path)
    # Simple heuristic suggestions: if task_type has many passes with no retries and claude tier > C0 sometimes -> suggest cap.
    by_type = defaultdict(list)
    for e in events[-200:]:
        if isinstance(e, dict) and e.get("type")=="outcome_ledger_event":
            by_type[e.get("task_type","unknown")].append(e)

    suggestions=[]
    for t, lst in by_type.items():
        if not lst:
            continue
        passes = sum(1 for e in lst if e.get("outcome",{}).get("status")=="pass" and e.get("outcome",{}).get("retries",0)==0)
        total = len(lst)
        any_high_tier = any((e.get("route",{}).get("claude_tier") not in (None,"","C0")) for e in lst)
        if total >= 5 and passes/total >= 0.9 and any_high_tier and len(suggestions)<3:
            suggestions.append({
                "task_type": t,
                "change": "Cap Claude tier to C0 unless repeat_failures>=2",
                "reason": "High success rate indicates higher Claude tiers are likely unnecessary.",
                "expected_savings": "high",
                "risk": "low"
            })

    out_spec = {
        "type":"route_autotune_suggestion",
        "generated_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
        "suggestions": suggestions
    }
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"route_autotune_suggest","status":"ok",
            "outputs":{"suggestion": out_spec, "count": len(suggestions)},
            "metrics":{"count": len(suggestions)}, "errors":[], "warnings":[]}
