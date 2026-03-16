#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import datetime

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    root = Path(inputs.get("root", "validation_runs")).resolve()
    date_str = inputs.get("date") or datetime.date.today().isoformat()
    run_dir = root / date_str
    subdirs = ["logs","artifacts","reports","specs"]
    created=[]
    for d in subdirs:
        p = run_dir / d
        p.mkdir(parents=True, exist_ok=True)
        created.append(str(p))
    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id": req.get("skill_id","evidence_init"),
        "status":"ok",
        "outputs":{
            "run_dir": str(run_dir),
            "created": created
        },
        "metrics":{"created_count": len(created)},
        "errors":[],
        "warnings":[]
    }
