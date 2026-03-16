"""Phase 38 — Indexer: scan scope, hash content, store; incremental (no diff if unchanged)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from claudeclockwork.kb.scope import in_scope
from claudeclockwork.kb.store import doc_id, index_path

def _content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def index_project(project_root: Path | str, kb_root: Path | str | None = None) -> dict[str, Any]:
    """Index in-scope files. Writes full index to kb_root. Re-index without changes produces no diffs."""
    root = Path(project_root).resolve()
    kb = Path(kb_root or root / ".clockwork_runtime" / "kb").resolve()
    kb.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for g in ["Docs/**/*", "mvps/**/*", ".claude/skills/**/manifest.json", ".claude/contracts/**/*"]:
        for f in root.glob(g):
            if not f.is_file():
                continue
            if not in_scope(f, root):
                continue
            try:
                data = f.read_bytes()
            except OSError:
                continue
            h = _content_hash(data)
            rel = str(f.relative_to(root)).replace("\\", "/")
            records.append({
                "doc_id": doc_id(rel, h),
                "path": rel,
                "content_hash": h,
                "metadata": {"title": f.stem},
            })
    by_path: dict[str, dict] = {r["path"]: r for r in records}
    idx = index_path(kb)
    with open(idx, "w", encoding="utf-8") as f:
        for r in by_path.values():
            f.write(json.dumps(r) + "\n")
    return {"indexed": len(by_path), "total": len(by_path)}
