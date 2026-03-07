#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    profile = inputs.get("profile")
    if not isinstance(profile, dict) or profile.get("type") != "route_profile_spec":
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"route_profile_update","status":"fail","outputs":{},
                "metrics":{}, "errors":["inputs.profile must be a route_profile_spec"], "warnings":[]}
    out = inputs.get("out",".clockwork_runtime/knowledge/route_profiles.json")
    p = Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    existing=[]
    if p.exists():
        try:
            existing = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            existing=[]
    if not isinstance(existing, list):
        existing=[]
    # replace by task_type
    task_type = profile.get("task_type")
    existing = [x for x in existing if isinstance(x, dict) and x.get("task_type") != task_type]
    existing.append(profile)
    p.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"route_profile_update","status":"ok",
            "outputs":{"out": str(p), "total": len(existing)}, "metrics":{"total": len(existing)},
            "errors":[], "warnings":[]}
