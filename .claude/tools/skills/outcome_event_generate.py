#!/usr/bin/env python3
from __future__ import annotations
import json, datetime
from pathlib import Path

def _safe_load(p: Path) -> dict:
    if not p.exists(): 
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    task_type = inputs.get("task_type","unknown")
    evidence_ref = inputs.get("evidence_ref","")
    routing_path = Path(inputs.get("routing_spec",""))
    qsig_path = Path(inputs.get("quality_signal",""))
    ledger_path = Path(inputs.get("ops_ledger_summary",""))

    routing = _safe_load(routing_path) if str(routing_path) else {}
    qsig = _safe_load(qsig_path) if str(qsig_path) else {}
    ledger = _safe_load(ledger_path) if str(ledger_path) else {}

    claude_tier = routing.get("claude_tier") or routing.get("models",{}).get("claude_tier","")
    local_model_tier = (routing.get("local_model_tier") or routing.get("oodle_tier")
                        or routing.get("models", {}).get("local_model_tier", "")
                        or routing.get("models", {}).get("oodle_tier", ""))
    status = qsig.get("status") or qsig.get("run_status") or "pass"
    retries = qsig.get("retries", 0)
    severity = qsig.get("severity_max","low")

    ev = {
      "type":"outcome_ledger_event",
      "timestamp": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
      "task_type": task_type,
      "route":{
        "doer": routing.get("doer",""),
        "verifier": routing.get("verifier",""),
        "relay": routing.get("relay",""),
        "claude_tier": claude_tier,
        "local_model_tier": local_model_tier
      },
      "outcome":{
        "status": status if status in ("pass","fail","blocked") else "pass",
        "retries": int(retries) if isinstance(retries,(int,float,str)) else 0,
        "severity_max": severity if severity in ("low","med","high","critical") else "low",
        "notes": "generated"
      },
      "metrics": ledger.get("waste", {}),
      "evidence_ref": evidence_ref
    }

    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"outcome_event_generate","status":"ok",
            "outputs":{"event": ev}, "metrics":{}, "errors":[], "warnings":[]}
