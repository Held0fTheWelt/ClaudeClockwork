#!/usr/bin/env python3
"""mutation_detect

Detect mutations between two snapshots: adds/removes/changes + rename heuristics.

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
        inputs = req.get("inputs", {})
        left = Path(inputs.get("left_root", "")).resolve()
        right = Path(inputs.get("right_root", "")).resolve()
        if not left.is_dir() or not right.is_dir():
            return _fail(req, [f"left_root/right_root must be directories. left={left} right={right}"])

        include_ext = inputs.get("include_ext") or [".py",".cpp",".h",".hpp",".md",".json",".yaml",".yml"]
        include_ext = [e.lower() for e in include_ext]
        output_path = inputs.get("output_path")

        def rel_map(root: Path) -> Dict[str,str]:
            m: Dict[str,str] = {}
            for fp in _list_files(root, include_ext=include_ext):
                rel = str(fp.relative_to(root))
                m[rel] = _sha256_bytes(fp.read_bytes())
            return m

        L = rel_map(left)
        R = rel_map(right)

        added = sorted([k for k in R.keys() if k not in L])
        removed = sorted([k for k in L.keys() if k not in R])
        changed = sorted([k for k in L.keys() if k in R and L[k] != R[k]])

        invL: Dict[str,List[str]] = {}
        for rel,h in L.items():
            invL.setdefault(h, []).append(rel)
        invR: Dict[str,List[str]] = {}
        for rel,h in R.items():
            invR.setdefault(h, []).append(rel)

        renames: List[Dict[str,str]] = []
        for h, lrels in invL.items():
            if h in invR:
                for lr in lrels:
                    for rr in invR[h]:
                        if lr != rr and lr in removed and rr in added:
                            renames.append({"from": lr, "to": rr, "hash": h})

        outputs = {
            "left_root": str(left),
            "right_root": str(right),
            "added": added,
            "removed": removed,
            "changed": changed,
            "renames_by_hash": renames,
        }

        if output_path:
            op=Path(output_path)
            lines = ["# Mutation Detection Report", "", f"Left: `{left}`", f"Right: `{right}`", ""]
            lines += [f"- Added: {len(added)}", f"- Removed: {len(removed)}", f"- Changed: {len(changed)}", f"- Renames (hash): {len(renames)}", ""]
            if renames:
                lines += ["## Suspected Renames", ""]
                for r in renames[:200]:
                    lines.append(f"- `{r['from']}` → `{r['to']}`")
            _write_text(op, "\n".join(lines) + "\n")
            outputs["output_path"]=str(op)

        return _ok(req, outputs, metrics={"left_files": len(L), "right_files": len(R)})
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
