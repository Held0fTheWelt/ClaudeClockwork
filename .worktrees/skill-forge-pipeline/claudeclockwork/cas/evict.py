"""Phase 36 — CAS eviction: quota-based, oldest-first, deterministic."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

INDEX_NAME = "index.jsonl"


def list_objects(cas_root: Path | str) -> list[tuple[str, float, int]]:
    """Return list of (content_hash, mtime, size) for all objects, sorted by mtime (oldest first)."""
    cas_root = Path(cas_root).resolve()
    objects_dir = cas_root / "objects"
    if not objects_dir.is_dir():
        return []
    out: list[tuple[str, float, int]] = []
    for prefix_dir in sorted(objects_dir.iterdir()):
        if not prefix_dir.is_dir():
            continue
        for f in prefix_dir.iterdir():
            if f.suffix == ".meta.json":
                continue
            try:
                mtime = f.stat().st_mtime
                size = f.stat().st_size
                out.append((f.name, mtime, size))
            except OSError:
                continue
    out.sort(key=lambda x: (x[1], x[0]))
    return out


def evict_to_quota(
    cas_root: Path | str,
    max_bytes: int | None = None,
    max_objects: int | None = None,
    pinned_hashes: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Evict oldest objects until under quota. Never evict pinned. Returns {evicted: int, freed_bytes: int}."""
    cas_root = Path(cas_root).resolve()
    pinned = pinned_hashes or frozenset()
    items = list_objects(cas_root)
    total_bytes = sum(s for _, _, s in items)
    total_objects = len(items)
    evicted = 0
    freed = 0
    for h, _mtime, size in items:
        if h in pinned:
            continue
        if max_bytes is not None and total_bytes <= max_bytes and (max_objects is None or total_objects <= max_objects):
            break
        p = cas_root / "objects" / h[:2] / h
        meta = p.with_suffix(p.suffix + ".meta.json")
        try:
            if p.is_file():
                p.unlink()
                evicted += 1
                freed += size
                total_bytes -= size
                total_objects -= 1
            if meta.is_file():
                meta.unlink()
        except OSError:
            continue
    return {"evicted": evicted, "freed_bytes": freed}
