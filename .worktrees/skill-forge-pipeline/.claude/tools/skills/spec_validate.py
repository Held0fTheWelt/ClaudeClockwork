#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator

def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    schema_path = Path(inputs["schema"]).resolve()
    examples = inputs.get("examples", [])
    if isinstance(examples, str):
        examples = [examples]
    root = Path(inputs.get("root",".")).resolve()
    # resolve examples relative to root if not absolute
    example_paths = []
    for ex in examples:
        p = Path(ex)
        if not p.is_absolute():
            p = (root / p).resolve()
        example_paths.append(p)
    schema = _load_json(schema_path)
    v = Draft202012Validator(schema)
    failures=[]
    for p in example_paths:
        inst = _load_json(p)
        errs = sorted(v.iter_errors(inst), key=lambda e: e.path)
        if errs:
            failures.append({
                "example": str(p),
                "errors": [f"{'/'.join([str(x) for x in e.path])}: {e.message}" for e in errs[:20]]
            })
    status = "ok" if not failures else "fail"
    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id": req.get("skill_id","spec_validate"),
        "status": status,
        "outputs": {"failures": failures},
        "metrics": {"failure_count": len(failures), "checked_count": len(example_paths)},
        "errors": [f"{len(failures)} examples failed validation"] if failures else [],
        "warnings": [],
    }
