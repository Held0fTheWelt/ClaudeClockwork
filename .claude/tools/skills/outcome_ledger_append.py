#!/usr/bin/env python3
from __future__ import annotations
import json, datetime
from pathlib import Path

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    event = inputs.get("event")
    if not isinstance(event, dict) or event.get("type") != "outcome_ledger_event":
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"outcome_ledger_append","status":"fail","outputs":{},
                "metrics":{}, "errors":["inputs.event must be an outcome_ledger_event"], "warnings":[]}

    out = Path(inputs.get("out",".llama_runtime/knowledge/outcome_ledger.jsonl"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.open("a", encoding="utf-8").write(json.dumps(event, ensure_ascii=False) + "\n")
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"outcome_ledger_append","status":"ok",
            "outputs":{"out": str(out)}, "metrics":{}, "errors":[], "warnings":[]}
