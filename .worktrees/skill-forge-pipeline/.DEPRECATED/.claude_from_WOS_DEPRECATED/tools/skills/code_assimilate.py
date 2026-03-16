#!/usr/bin/env python3
"""code_assimilate

Draft an integration plan to assimilate foreign code into a host framework.

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
        foreign_root=Path(inputs.get("foreign_root","")).resolve()
        host_root=Path(inputs.get("host_root","")).resolve()
        if not foreign_root.is_dir() or not host_root.is_dir():
            return _fail(req, [f"foreign_root/host_root must be directories. foreign={foreign_root} host={host_root}"])

        target_namespace=str(inputs.get("target_namespace") or "host")
        output_path=inputs.get("output_path")

        def topdirs(root: Path) -> List[str]:
            s=set()
            for fp in _list_files(root):
                rel=str(fp.relative_to(root))
                s.add(rel.split(os.sep)[0])
            return sorted(s)

        plan = {
            "foreign_root": str(foreign_root),
            "host_root": str(host_root),
            "foreign_topdirs": topdirs(foreign_root),
            "host_topdirs": topdirs(host_root),
            "target_namespace": target_namespace,
            "strategy": [
                "Identify foreign boundaries and entrypoints",
                "Map host extension points and contracts",
                "Introduce adapter layer, avoid forking core",
                "Port incrementally with tests and feature flags",
            ],
            "open_questions": [
                "Host extension points?",
                "Foreign dependencies/licenses?",
                "Test strategy and rollout plan?"
            ]
        }

        if output_path:
            op=Path(output_path)
            md=["# Code Assimilation Plan","", f"Foreign: `{foreign_root}`", f"Host: `{host_root}`", ""]
            md += ["## Strategy"] + [f"- {s}" for s in plan["strategy"]] + [""]
            md += ["## Foreign top dirs"] + [f"- `{d}`" for d in plan["foreign_topdirs"]] + [""]
            md += ["## Host top dirs"] + [f"- `{d}`" for d in plan["host_topdirs"]] + [""]
            md += ["## Open questions"] + [f"- {q}" for q in plan["open_questions"]] + [""]
            _write_text(op, "\n".join(md)+"\n")
            plan["output_path"]=str(op)

        return _ok(req, plan, metrics={"foreign_files": len(_list_files(foreign_root)), "host_files": len(_list_files(host_root))})
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
