#!/usr/bin/env python3
"""copyright_standardize

Check file headers against a copyright/license standard.

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
        root=Path(inputs.get("root",".")).resolve()
        if not root.is_dir():
            return _fail(req,[f"inputs.root is not a directory: {root}"])
        template_regex=str(inputs.get("template_regex") or r"Copyright\s*\(c\)\s*\d{4}")
        include_ext=inputs.get("include_ext") or [".py",".cpp",".h",".hpp",".cs",".js",".ts",".md"]
        include_ext=[e.lower() for e in include_ext]
        output_path=inputs.get("output_path")

        rx=re.compile(template_regex, re.IGNORECASE)
        missing=[]
        files=_list_files(root, include_ext=include_ext)
        for fp in files:
            head=_read_text(fp)[:500]
            if not rx.search(head):
                missing.append(str(fp))

        outputs={"root": str(root), "template_regex": template_regex, "missing_headers": missing, "missing_count": len(missing)}
        if output_path:
            op=Path(output_path)
            md=["# Copyright Header Report","", f"Root: `{root}`","", f"Missing: **{len(missing)}**",""]
            for fp in missing[:300]:
                md.append(f"- `{fp}`")
            _write_text(op, "\n".join(md)+"\n")
            outputs["output_path"]=str(op)

        return _ok(req, outputs, metrics={"files_scanned": len(files), "missing": len(missing)})
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
