#!/usr/bin/env python3
"""skill_registry_search

Search skill registry + tools by keywords (meta).

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
def _find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(25):
        if (cur / ".claude").is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()

def run(req: dict) -> dict:
    try:
        inputs=req.get("inputs", {})
        repo_root = Path(inputs.get("repo_root") or _find_repo_root(Path.cwd())).resolve()
        query = str(inputs.get("query") or "").strip()
        if not query:
            return _fail(req, ["inputs.query is required"])
        max_results=int(inputs.get("max_results") or 25)

        registry_path = repo_root / ".claude" / "skills" / "registry.md"
        tools_root = repo_root / ".claude" / "tools" / "skills"

        hay=""
        if registry_path.exists():
            hay += _read_text(registry_path) + "\n"
        if tools_root.is_dir():
            for fn in sorted([p.name for p in tools_root.glob("*.py")]):
                hay += fn + "\n"

        qwords=[w.lower() for w in re.split(r"\W+", query) if w.strip()]
        lines=hay.splitlines()
        scored=[]
        for ln in lines:
            lnl=ln.lower()
            score=sum(1 for w in qwords if w in lnl)
            if score>0:
                scored.append((score, ln.strip()))
        scored.sort(key=lambda t: (-t[0], t[1]))
        results=[ln for _,ln in scored[:max_results]]

        tool_hits=[]
        if tools_root.is_dir():
            for p in tools_root.glob("*.py"):
                base=p.stem.lower()
                if any(w in base for w in qwords):
                    tool_hits.append(p.name)

        outputs={"repo_root": str(repo_root), "query": query, "results": results, "tool_hits": sorted(set(tool_hits))}
        return _ok(req, outputs)
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
