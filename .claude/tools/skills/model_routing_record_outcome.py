#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {"version":1,"models":{}}

def _save(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    run_id = str(inputs.get("run_id","run-unknown"))
    task_type = str(inputs.get("task_type","general"))
    model = str(inputs.get("model","unknown"))
    success = bool(inputs.get("success", False))
    quality = float(inputs.get("quality_0_10", 0.0))
    total_tokens = int(inputs.get("total_tokens", 0))
    notes = str(inputs.get("notes",""))
    stats_path = Path(inputs.get("stats_path",".clockwork_runtime/brain/model_routing_stats.json")).resolve()

    stats = _load(stats_path)
    m = stats.setdefault("models", {}).setdefault(model, {})
    tt = m.setdefault("task_types", {}).setdefault(task_type, {"attempts":0,"successes":0,"failures":0,"avg_tokens":0.0,"avg_quality":0.0})
    tt["attempts"] = int(tt.get("attempts",0)) + 1
    if success:
        tt["successes"] = int(tt.get("successes",0)) + 1
    else:
        tt["failures"] = int(tt.get("failures",0)) + 1
    # update averages
    n = tt["attempts"]
    tt["avg_tokens"] = float(((tt.get("avg_tokens",0.0)*(n-1)) + total_tokens) / max(1,n))
    tt["avg_quality"] = float(((tt.get("avg_quality",0.0)*(n-1)) + quality) / max(1,n))
    tt["last_run_id"] = run_id
    tt["last_notes"] = notes
    tt["updated_at"] = datetime.utcnow().replace(microsecond=0).isoformat()+"Z"

    _save(stats_path, stats)

    out_dir = Path(".report")/"routing"/run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir/f"model_routing_outcome_{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    out.write_text(json.dumps({
        "type":"model_routing_outcome",
        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
        "run_id": run_id,
        "task_type": task_type,
        "model": model,
        "success": success,
        "quality_0_10": quality,
        "total_tokens": total_tokens,
        "notes": notes
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"model_routing_record_outcome",
        "status":"ok",
        "outputs":{
            "stats_path": str(stats_path),
            "outcome_path": str(out)
        },
        "errors": [],
        "warnings": [],
        "metrics":{
            "attempts": tt["attempts"],
            "success_rate": (tt["successes"]/max(1,tt["attempts"]))
        }
    }
