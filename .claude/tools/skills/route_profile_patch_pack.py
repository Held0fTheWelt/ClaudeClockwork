#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    suggestion = inputs.get("suggestion")
    if not isinstance(suggestion, dict) or suggestion.get("type") != "route_autotune_suggestion":
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"route_profile_patch_pack","status":"fail","outputs":{},
                "metrics":{}, "errors":["inputs.suggestion must be RouteAutotuneSuggestion"], "warnings":[]}

    out_dir = Path(inputs.get("out_dir",".claude/proposals/route_profile_patches"))
    out_dir.mkdir(parents=True, exist_ok=True)

    patches=[]
    for i, s in enumerate((suggestion.get("suggestions") or [])[:3], start=1):
        patch = {
          "type":"route_profile_spec",
          "task_type": s.get("task_type","unknown"),
          "preferred_route": {"doer":"Claude C0 doer","verifier":"Tool-first + O3 only on triggers","relay":"Claude C0 relay",
                              "notes": s.get("change","")},
          "fallbacks":["Escalate verifier depth","Then escalate Claude to C1"],
          "signals":["repeat_failures>=2","over_escalations>=1"]
        }
        p = out_dir / f"route_profile_patch_{i}_{patch['task_type']}.json"
        p.write_text(json.dumps(patch, indent=2, ensure_ascii=False), encoding="utf-8")
        patches.append(str(p))

    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"route_profile_patch_pack","status":"ok",
            "outputs":{"patch_files": patches},
            "metrics":{"count": len(patches)}, "errors":[], "warnings":[]}
