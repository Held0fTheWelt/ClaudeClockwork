"""Phase 36 — CAS store: put/get, integrity, reuse."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.cas.store import put, get, get_metadata, exists


def test_put_get_same_hash() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        h1 = put(root, b"hello")
        h2 = put(root, b"hello")
        assert h1 == h2
        assert get(root, h1) == b"hello"


def test_get_integrity_fail() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        h = put(root, b"x")
        obj_dir = root / "objects" / h[:2]
        (obj_dir / h).write_bytes(b"y")
        assert get(root, h) is None


def test_reuse_across_runs() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        h = put(root, b"artifact", metadata={"producer": "node_1"})
        assert exists(root, h)
        meta = get_metadata(root, h)
        assert meta and meta.get("producer") == "node_1"