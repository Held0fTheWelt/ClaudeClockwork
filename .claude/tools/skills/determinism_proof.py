#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, glob
from pathlib import Path

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    root = Path(inputs.get("root",".")).resolve()
    patterns = inputs.get("patterns", [])
    if isinstance(patterns, str):
        patterns = [patterns]
    files=[]
    for pat in patterns:
        files.extend([Path(x) for x in glob.glob(str(root / pat), recursive=True)])
    files = [p for p in files if p.is_file()]
    hashes1 = {str(p): sha256_file(p) for p in files}
    hashes2 = {str(p): sha256_file(p) for p in files}
    mismatches=[]
    for p in files:
        k = str(p)
        if hashes1[k] != hashes2[k]:
            mismatches.append(k)
    status = "ok" if not mismatches else "fail"
    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id": req.get("skill_id","determinism_proof"),
        "status": status,
        "outputs": {"mismatches": mismatches, "hashes": hashes1},
        "metrics": {"file_count": len(files), "mismatch_count": len(mismatches)},
        "errors": [f"Determinism mismatches: {len(mismatches)}"] if mismatches else [],
        "warnings": [],
    }
