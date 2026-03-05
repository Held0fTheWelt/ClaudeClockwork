#!/usr/bin/env python3
"""system_map

Map module/framework connections via imports/includes and emit Mermaid.

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
        include_ext=inputs.get("include_ext") or [".py",".cpp",".h",".hpp",".cs",".js",".ts"]
        include_ext=[e.lower() for e in include_ext]
        output_path=inputs.get("output_path")

        files=_list_files(root, include_ext=include_ext)
        edges: Dict[Tuple[str,str], int] = {}
        node_of=lambda rel: rel.split(os.sep)[0] if os.sep in rel else rel

        import_re=re.compile(r"^\s*(import\s+([\w\.]+)|from\s+([\w\.]+)\s+import)", re.MULTILINE)
        include_re=re.compile(r"^\s*#include\s+[<\"]([^>\"]+)[>\"]", re.MULTILINE)

        for fp in files:
            rel=str(fp.relative_to(root))
            a=node_of(rel)
            txt=_read_text(fp)
            for m in import_re.finditer(txt):
                mod=m.group(2) or m.group(3) or ""
                b=mod.split(".")[0] if mod else ""
                if b and b!=a:
                    edges[(a,b)]=edges.get((a,b),0)+1
            for m in include_re.finditer(txt):
                inc=m.group(1)
                b=inc.split("/")[0]
                if b and b!=a:
                    edges[(a,b)]=edges.get((a,b),0)+1

        mermaid=["flowchart LR"]
        for (a,b),w in sorted(edges.items(), key=lambda kv: kv[1], reverse=True)[:200]:
            mermaid.append(f"  {a} -->|{w}| {b}")

        outputs={
            "root": str(root),
            "edges": [{"from":a,"to":b,"weight":w} for (a,b),w in edges.items()],
            "mermaid":"\n".join(mermaid),
        }

        if output_path:
            op=Path(output_path)
            md=["# System Map","", "```mermaid", outputs["mermaid"], "```", ""]
            _write_text(op, "\n".join(md)+"\n")
            outputs["output_path"]=str(op)

        return _ok(req, outputs, metrics={"files_scanned": len(files), "edges": len(edges)})
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
