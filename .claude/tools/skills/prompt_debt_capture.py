#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    items = inputs.get("items", [])
    if not isinstance(items, list) or not items:
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"prompt_debt_capture","status":"fail","outputs":{},
                "metrics":{}, "errors":["inputs.items must be a non-empty list"], "warnings":[]}
    items = items[:5]
    out_path = inputs.get("out","")
    if out_path:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"prompt_debt_capture","status":"ok",
            "outputs":{"count": len(items), "out": out_path},
            "metrics":{"count": len(items)}, "errors":[], "warnings":[]}
