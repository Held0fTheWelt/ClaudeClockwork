"""Phase 36 — CAS: put/get by content hash under runtime root; integrity verification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

def _hash_content(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _object_path(cas_root: Path, content_hash: str) -> Path:
    prefix = content_hash[:2]
    return cas_root / "objects" / prefix / content_hash


def put(cas_root: Path | str, data: bytes, metadata: dict[str, Any] | None = None) -> str:
    """Store data; return content hash. Metadata stored alongside."""
    cas_root = Path(cas_root).resolve()
    h = _hash_content(data)
    p = _object_path(cas_root, h)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    meta_path = p.with_suffix(p.suffix + ".meta.json")
    meta = metadata or {}
    meta.setdefault("size", len(data))
    meta_path.write_text(json.dumps(meta) + "\n", encoding="utf-8")
    return h


def get(cas_root: Path | str, content_hash: str) -> bytes | None:
    """Return object bytes if present; None if missing or corrupt."""
    cas_root = Path(cas_root).resolve()
    p = _object_path(cas_root, content_hash)
    if not p.is_file():
        return None
    data = p.read_bytes()
    if _hash_content(data) != content_hash:
        return None
    return data


def get_metadata(cas_root: Path | str, content_hash: str) -> dict[str, Any] | None:
    """Return stored metadata for object."""
    cas_root = Path(cas_root).resolve()
    p = _object_path(cas_root, content_hash)
    meta_path = p.with_suffix(p.suffix + ".meta.json")
    if not meta_path.is_file():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def exists(cas_root: Path | str, content_hash: str) -> bool:
    """True if object exists and hash matches."""
    return get(cas_root, content_hash) is not None
