#!/usr/bin/env python3
"""mechanic_explain

Generate a structured mechanic explanation scaffold from evidence files.

Interface: run(req: dict) -> SkillResultSpec
- Reads req["inputs"]
- Writes optional markdown to inputs["output_path"]

Deterministic local-file tool. No network.
"""

from __future__ import annotations

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _list_files(root: Path, include_ext: Optional[List[str]] = None) -> List[Path]:
    out: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {'.git','.svn','.hg','__pycache__','.pytest_cache','node_modules','.venv'}]
        for fn in filenames:
            p = Path(dirpath) / fn
            if include_ext and p.suffix.lower() not in include_ext:
                continue
            out.append(p)
    return out

def _ok(req: dict, outputs: dict, warnings: Optional[List[str]] = None, metrics: Optional[dict] = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", ""),
        "status": "ok",
        "outputs": outputs,
        "errors": [],
        "warnings": warnings or [],
        "metrics": metrics or {},
    }

def _fail(req: dict, errors: List[str], warnings: Optional[List[str]] = None, metrics: Optional[dict] = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", ""),
        "status": "fail",
        "outputs": {},
        "errors": errors,
        "warnings": warnings or [],
        "metrics": metrics or {},
    }
def run(req: dict) -> dict:
    try:
        inputs=req.get("inputs", {})
        name=str(inputs.get("name") or "Mechanic")
        evidence_paths=inputs.get("evidence_paths") or []
        output_path=inputs.get("output_path")

        excerpts=[]
        for p in evidence_paths[:30]:
            pp=Path(p)
            if pp.exists() and pp.is_file():
                txt=_read_text(pp)
                excerpts.append({"path": str(pp), "preview": txt[:800], "sha256": _sha256_bytes(txt.encode("utf-8", errors="replace"))})

        md = [
            f"# Mechanic: {name}",
            "",
            "## What it does",
            "-",
            "",
            "## Control flow",
            "1.",
            "",
            "## State & data",
            "-",
            "",
            "## Extension points",
            "-",
            "",
            "## Failure modes",
            "-",
            "",
            "## Verification",
            "-",
            "",
            "## Evidence",
        ]
        for ex in excerpts:
            md += ["", f"### {ex['path']}", f"- sha256: `{ex['sha256']}`", "", "```", ex["preview"], "```"]

        outputs={"name": name, "evidence": [{"path":e["path"],"sha256":e["sha256"]} for e in excerpts]}
        if output_path:
            op=Path(output_path)
            _write_text(op, "\n".join(md)+"\n")
            outputs["output_path"]=str(op)
        else:
            outputs["markdown"]="\n".join(md)+"\n"

        return _ok(req, outputs, metrics={"evidence_files": len(excerpts)})
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
