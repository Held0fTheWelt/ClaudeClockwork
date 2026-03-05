#!/usr/bin/env python3
"""reference_fix

Detect (and optionally rewrite) broken markdown links after folder moves.

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
        docs_root=Path(inputs.get("docs_root") or root).resolve()
        if not root.is_dir() or not docs_root.is_dir():
            return _fail(req, [f"root/docs_root must be directories. root={root} docs_root={docs_root}"])
        dry_run=bool(inputs.get("dry_run", True))
        move_map=inputs.get("move_map") or {}
        output_path=inputs.get("output_path")

        md_files=_list_files(docs_root, include_ext=[".md"])
        link_re=re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        broken=[]
        fixed=[]

        def resolve(md_path: Path, target: str) -> Optional[Path]:
            if target.startswith(("http://","https://","mailto:")):
                return None
            t=target.split("#")[0]
            if not t:
                return None
            if t.startswith("/"):
                return root / t.lstrip("/")
            return (md_path.parent / t).resolve()

        for fp in md_files:
            txt=_read_text(fp)
            for m in link_re.finditer(txt):
                target=m.group(1).strip()
                abs_path=resolve(fp, target)
                if abs_path and not abs_path.exists():
                    broken.append({"file": str(fp), "link": target, "resolved": str(abs_path)})

            if move_map:
                new_txt=txt
                for oldp,newp in move_map.items():
                    new_txt=re.sub(rf"(\]\()({re.escape(oldp)}[^)#]*)([#)]?)",
                                   lambda mm: mm.group(1)+newp+mm.group(3),
                                   new_txt)
                if new_txt!=txt and not dry_run:
                    _write_text(fp, new_txt)
                    fixed.append({"file": str(fp), "changes":"applied move_map rewrites"})

        outputs={"root": str(root), "docs_root": str(docs_root), "dry_run": dry_run, "broken_links": broken, "broken_count": len(broken), "fixed": fixed}
        if output_path:
            op=Path(output_path)
            md=["# Broken Reference Report","", f"Docs root: `{docs_root}`","", f"Broken links: **{len(broken)}**",""]
            for b in broken[:300]:
                md.append(f"- `{b['file']}` → `{b['link']}` (missing `{b['resolved']}`)")
            if fixed:
                md += ["", "## Applied fixes", ""]
                for f in fixed[:200]:
                    md.append(f"- `{f['file']}` — {f['changes']}")
            _write_text(op, "\n".join(md)+"\n")
            outputs["output_path"]=str(op)

        return _ok(req, outputs, metrics={"md_files": len(md_files), "broken": len(broken), "fixed": len(fixed)})
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
