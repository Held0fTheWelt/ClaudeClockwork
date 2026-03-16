#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    claude_root = Path(inputs.get("claude_root", ".claude")).resolve()

    schemas_dir = claude_root / "contracts/schemas"
    examples_dir = claude_root / "contracts/examples"

    # Hard fail if contract folders are missing (prevents false-green 0/0 checks)
    missing_dirs = [str(p) for p in (schemas_dir, examples_dir) if not p.exists()]
    if missing_dirs:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "schema_batch_validate"),
            "status": "fail",
            "outputs": {"missing_dirs": missing_dirs},
            "errors": ["Contract directories missing"],
            "warnings": [],
            "metrics": {},
        }

    schemas = sorted(schemas_dir.glob("*.schema.json"))
    examples = sorted([p for p in examples_dir.glob("*.example.json")])

    failures = []
    missing_examples = []

    # map base name -> example
    ex_map = {p.name.replace(".example.json", ""): p for p in examples}

    checked = 0
    for s in schemas:
        base = s.name.replace(".schema.json", "")
        ex = ex_map.get(base)
        if not ex:
            missing_examples.append(str(examples_dir / f"{base}.example.json"))
            continue
        try:
            schema = _load_json(s)
            inst = _load_json(ex)
            v = Draft202012Validator(schema)
            errs = list(v.iter_errors(inst))
            if errs:
                failures.append({"schema": str(s), "example": str(ex), "errors": [e.message for e in errs[:20]]})
        except Exception as e:
            failures.append({"schema": str(s), "example": str(ex), "errors": [str(e)]})
        checked += 1

    status = "ok" if (not failures and not missing_examples) else "fail"

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "schema_batch_validate"),
        "status": status,
        "outputs": {
            "schemas": len(schemas),
            "examples": len(examples),
            "checked": checked,
            "failures": failures,
            "missing_examples": missing_examples,
        },
        "metrics": {"schemas": len(schemas), "examples": len(examples), "checked": checked, "failure_count": len(failures), "missing_examples": len(missing_examples)},
        "errors": ["Schema batch validation failed"] if status == "fail" else [],
        "warnings": [],
    }
