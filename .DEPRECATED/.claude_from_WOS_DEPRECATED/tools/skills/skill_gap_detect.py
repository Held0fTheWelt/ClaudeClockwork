#!/usr/bin/env python3
"""skill_gap_detect

Detect capability gaps for an intent (meta).

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
        intent = str(inputs.get("intent") or "").strip()
        if not intent:
            return _fail(req, ["inputs.intent is required"])

        keywords = inputs.get("keywords")
        if not keywords:
            keywords = [w for w in re.split(r"\W+", intent) if len(w) >= 4][:12]
        keywords=[k.lower() for k in keywords]
        min_match=int(inputs.get("min_match") or 2)

        registry_path = repo_root / ".claude" / "skills" / "registry.md"
        tools_root = repo_root / ".claude" / "tools" / "skills"

        corpus=""
        if registry_path.exists():
            corpus += _read_text(registry_path).lower() + "\n"
        if tools_root.is_dir():
            corpus += "\n".join([p.name.lower() for p in tools_root.glob("*.py")]) + "\n"

        match_count=sum(1 for k in keywords if k in corpus)
        covered = match_count >= min_match

        suggestion=None
        if not covered:
            base=re.sub(r"[^a-zA-Z0-9]+"," ", intent).strip().lower()
            words=[w for w in base.split() if w][:6]
            skill_name="_".join(words) if words else "new_skill"
            if not re.match(r"^[a-z]", skill_name):
                skill_name="skill_"+skill_name
            suggestion={
                "skill_name": skill_name,
                "one_liner": intent[:120],
                "recommended_inputs": [
                    {"name":"root","type":"string","description":"Root directory"},
                    {"name":"output_path","type":"string","description":"Optional markdown report"},
                    {"name":"dry_run","type":"boolean","description":"Do not modify files"},
                ]
            }

        outputs={"repo_root": str(repo_root), "intent": intent, "keywords": keywords, "match_count": match_count, "covered": covered, "suggestion": suggestion}
        return _ok(req, outputs)
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
