#!/usr/bin/env python3
"""log_standardize

Lint logging usage and conventions (first-pass).

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
            return _fail(req, [f"inputs.root is not a directory: {root}"])
        rules = inputs.get("rules") or {"disallow_print": True, "require_ue_log_category": True}
        output_path=inputs.get("output_path")

        files=_list_files(root, include_ext=[".py",".cpp",".h",".hpp",".cs",".js",".ts"])
        issues=[]
        for fp in files:
            txt=_read_text(fp)
            if rules.get("disallow_print") and re.search(r"\bprint\s*\(", txt):
                issues.append({"file": str(fp), "type":"print_usage", "hint":"Use logger instead of print()."})
            if rules.get("require_ue_log_category") and re.search(r"\bUE_LOG\s*\(\s*,", txt):
                issues.append({"file": str(fp), "type":"missing_ue_log_category", "hint":"UE_LOG first arg should be a category."})

        outputs={"root": str(root), "rules": rules, "issues": issues, "issue_count": len(issues)}
        if output_path:
            op=Path(output_path)
            md=["# Log Standardization Report","", f"Root: `{root}`","", f"Issues: **{len(issues)}**",""]
            for it in issues[:300]:
                md.append(f"- `{it['type']}` — `{it['file']}` — {it['hint']}")
            _write_text(op, "\n".join(md)+"\n")
            outputs["output_path"]=str(op)

        return _ok(req, outputs, metrics={"files_scanned": len(files), "issues": len(issues)})
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
