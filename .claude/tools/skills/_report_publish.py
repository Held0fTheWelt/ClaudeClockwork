#!/usr/bin/env python3
from __future__ import annotations
import shutil
from pathlib import Path

def publish_files(run_id: str, category: str, files: list[str], prefix: str) -> list[str]:
    """
    Copy artifacts into `.report/<category>/<run_id>/` with a stable prefix.
    Returns list of published paths.
    """
    out_dir = Path(".report") / category / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    published = []
    for f in files:
        if not f:
            continue
        p = Path(f)
        if not p.exists():
            continue
        dst = out_dir / (prefix + "_" + p.name)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        published.append(str(dst))
    return published
