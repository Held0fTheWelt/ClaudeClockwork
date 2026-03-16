#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    # tool expects already written hypotheses as short dicts (from a cheap LLM or human)
    hypotheses = inputs.get("hypotheses", [])
    if not isinstance(hypotheses, list) or not hypotheses:
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"hypothesis_builder","status":"fail","outputs":{},
                "metrics":{}, "errors":["inputs.hypotheses must be a non-empty list"], "warnings":[]}
    # enforce max 3
    hypotheses = hypotheses[:3]
    spec = {"type":"hypothesis_spec","id": inputs.get("id","hyp-auto"),
            "context": inputs.get("context",""), "hypotheses": hypotheses}
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"hypothesis_builder","status":"ok","outputs":{"hypothesis_spec": spec},
            "metrics":{"count": len(hypotheses)}, "errors":[], "warnings":[]}
