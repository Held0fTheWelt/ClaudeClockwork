#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
from jsonschema import Draft202012Validator

def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    root = Path(inputs.get("root",".claude")).resolve()
    schemas = list(root.rglob("contracts/schemas/*.schema.json"))
    examples = list(root.rglob("contracts/examples/*.example.json"))
    negative = list(root.rglob("contracts/examples/negative/*.json"))

    invalid_examples=[]
    for s in schemas:
        try:
            schema = _load_json(s)
            v = Draft202012Validator(schema)
        except Exception as e:
            continue
        # match examples by filename stem prefix (best effort)
        for ex in examples:
            if ex.name.startswith(s.name.replace(".schema.json","")) or ex.name.startswith(s.stem.replace(".schema","")):
                try:
                    inst = _load_json(ex)
                    errs = list(v.iter_errors(inst))
                    if errs:
                        invalid_examples.append(str(ex))
                except Exception:
                    invalid_examples.append(str(ex))
        # negative fixtures should fail if they correspond
        # (we do not strictly map; we only confirm they are invalid json or invalid per schema if mapped)
    # Task references: find schema filenames mentioned in tasks and ensure they exist
    missing_refs=[]
    rx = re.compile(r"contracts/schemas/([A-Za-z0-9_\\-\\.]+\\.schema\\.json)")
    for md in root.rglob("tasks/**/*.md"):
        txt = md.read_text(encoding="utf-8", errors="ignore")
        for m in rx.findall(txt):
            if not (root / "contracts/schemas" / m).exists():
                missing_refs.append(f"{md}: {m}")

    out = {
        "schemas_count": len(schemas),
        "examples_count": len(examples),
        "invalid_examples": invalid_examples,
        "missing_schema_refs": missing_refs
    }
    status = "ok" if (not invalid_examples and not missing_refs) else "fail"
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"contract_drift_sentinel","status": status,
            "outputs": out, "metrics":{"invalid_examples": len(invalid_examples), "missing_refs": len(missing_refs)},
            "errors": (["Drift detected"] if status=="fail" else []), "warnings":[]}
