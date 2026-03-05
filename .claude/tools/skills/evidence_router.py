#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import fnmatch

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    action = inputs.get("requested_action","")
    root = Path(inputs.get("evidence_root","validation_runs")).resolve()
    signals = inputs.get("signals", [])
    if isinstance(signals, str):
        signals = [signals]

    include=[]
    snippets=[]
    exclude=["node_modules/","*.zip","*.png","*.jpg","*.jpeg"]

    # Deterministic selection:
    # - always include specs/reports if present
    for pat in ["**/specs/*.json","**/reports/*.json","**/reports/*.md","**/specs/*.md"]:
        for p in root.glob(pat):
            if p.is_file():
                include.append(str(p))

    # add log tail if deep_oodle or failures
    if action in ("deep_oodle","decision_feedback") or any("fail" in s for s in signals) or any("repeat_failures" in s for s in signals):
        for p in root.glob("**/logs/*.log"):
            if p.is_file():
                snippets.append({"source": str(p), "range":"tail:200", "why":"recent log context"})
                break

    selection = {
        "type":"evidence_selection_spec",
        "selection_id": inputs.get("selection_id","es-auto"),
        "requested_action": action or "unknown",
        "include": sorted(list(dict.fromkeys(include)))[:50],
        "snippets": snippets[:5],
        "exclude": exclude,
        "reason": "tool-first deterministic evidence selection"
    }

    return {"type":"skill_result_spec",
            "request_id": req.get("request_id",""),
            "skill_id":"evidence_router",
            "status":"ok",
            "outputs":{"selection": selection},
            "metrics":{"include_count": len(selection["include"]), "snippets": len(selection["snippets"])},
            "errors":[],
            "warnings":[]}
