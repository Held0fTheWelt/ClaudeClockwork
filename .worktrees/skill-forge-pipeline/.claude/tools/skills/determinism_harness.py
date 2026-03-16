#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _norm_text(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def _digest_file(p: Path, normalize_json: bool) -> str:
    data = p.read_bytes()

    if normalize_json and p.suffix.lower() in {".json", ".jsonl"}:
        try:
            if p.suffix.lower() == ".jsonl":
                lines = [json.loads(line) for line in data.decode("utf-8", errors="ignore").splitlines() if line.strip()]
                norm = "\n".join(json.dumps(o, sort_keys=True, ensure_ascii=False) for o in lines) + "\n"
            else:
                obj = json.loads(data.decode("utf-8", errors="ignore"))
                norm = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            data = norm.encode("utf-8")
        except Exception:
            pass

    data = _norm_text(data)
    return hashlib.sha256(data).hexdigest()


def _digest_dir(p: Path, normalize_json: bool) -> str:
    h = hashlib.sha256()
    for f in sorted([x for x in p.rglob("*") if x.is_file()]):
        rel = f.relative_to(p)
        h.update(str(rel).encode("utf-8"))
        h.update(_digest_file(f, normalize_json).encode("utf-8"))
    return h.hexdigest()


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    targets = inputs.get("targets", [])
    if isinstance(targets, str):
        targets = [targets]
    normalize_json = bool(inputs.get("normalize_json", True))

    digests = []
    missing = 0
    for t in targets:
        p = Path(t).resolve()
        if not p.exists():
            digests.append({"target": t, "exists": False, "digest": ""})
            missing += 1
            continue
        digest = _digest_dir(p, normalize_json) if p.is_dir() else _digest_file(p, normalize_json)
        digests.append({"target": str(p), "exists": True, "digest": digest})

    status = "ok" if missing == 0 else "fail"

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "determinism_harness"),
        "status": status,
        "outputs": {"digests": digests},
        "metrics": {"targets": len(digests), "missing": missing},
        "errors": [f"Missing targets: {missing}"] if missing else [],
        "warnings": [],
    }
