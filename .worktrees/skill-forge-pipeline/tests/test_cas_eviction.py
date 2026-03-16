"""Phase 36 — CAS eviction: quota, deterministic order, pinned."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.cas.store import put, get
from claudeclockwork.cas.evict import list_objects, evict_to_quota


def test_evict_to_quota() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        put(root, b"a" * 10)
        put(root, b"b" * 10)
        put(root, b"c" * 10)
        out = evict_to_quota(root, max_bytes=25, max_objects=10)
        assert out.get("evicted", 0) >= 1
        assert out.get("freed_bytes", 0) >= 10


def test_pinned_not_evicted() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        h1 = put(root, b"pin")
        h2 = put(root, b"evict")
        evict_to_quota(root, max_objects=1, pinned_hashes=frozenset({h1}))
        assert get(root, h1) == b"pin"
        # h2 may or may not be evicted depending on order