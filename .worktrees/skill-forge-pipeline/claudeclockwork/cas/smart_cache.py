"""Phase 50 — Smart caching: cross-project reuse via bundles, pinning, provenance, poisoning protection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claudeclockwork.cas.store import get, put, get_metadata, exists


PIN_FILE = "pinned_hashes.json"
PROVENANCE_KEYS = ("source_bundle_id", "project_id")


def pin(cas_root: Path | str, content_hash: str) -> None:
    """Add hash to pinned set (allowed for cross-project reuse)."""
    root = Path(cas_root).resolve()
    pin_path = root / PIN_FILE
    pinned: set[str] = set()
    if pin_path.is_file():
        try:
            data = json.loads(pin_path.read_text(encoding="utf-8"))
            pinned = set(data.get("hashes", []))
        except (OSError, json.JSONDecodeError):
            pass
    pinned.add(content_hash)
    pin_path.parent.mkdir(parents=True, exist_ok=True)
    pin_path.write_text(json.dumps({"hashes": sorted(pinned)}) + "\n", encoding="utf-8")


def get_pinned(cas_root: Path | str) -> set[str]:
    """Return set of pinned content hashes."""
    root = Path(cas_root).resolve()
    pin_path = root / PIN_FILE
    if not pin_path.is_file():
        return set()
    try:
        data = json.loads(pin_path.read_text(encoding="utf-8"))
        return set(data.get("hashes", []))
    except (OSError, json.JSONDecodeError):
        return set()


def put_with_provenance(
    cas_root: Path | str,
    data: bytes,
    source_bundle_id: str = "",
    project_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> str:
    """Store data with provenance metadata. Returns content hash."""
    meta = dict(metadata or {})
    if source_bundle_id:
        meta["source_bundle_id"] = source_bundle_id
    if project_id:
        meta["project_id"] = project_id
    return put(cas_root, data, metadata=meta)


def get_safe(
    cas_root: Path | str,
    content_hash: str,
    allowed_bundles: set[str] | None = None,
    require_pinned: bool = True,
) -> bytes | None:
    """
    Get object only if allowed (poisoning protection). If require_pinned, hash must be in pinned set.
    If allowed_bundles is set, provenance source_bundle_id must be in allowed_bundles.
    """
    root = Path(cas_root).resolve()
    if require_pinned and content_hash not in get_pinned(root):
        return None
    meta = get_metadata(root, content_hash)
    if allowed_bundles is not None and meta:
        src = meta.get("source_bundle_id")
        if src and src not in allowed_bundles:
            return None
    return get(root, content_hash)
