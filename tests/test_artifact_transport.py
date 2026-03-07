"""Phase 35 — Artifact transport (bundle pack/unpack, hash verification)."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.workers.artifact_transport import pack_bundle, unpack_bundle, hash_content


def test_pack_unpack_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "src"
        src.mkdir()
        (src / "a.txt").write_text("hello", encoding="utf-8")
        out_zip = Path(d) / "out.zip"
        pack = pack_bundle(src, out_zip, redact=False)
        assert "a.txt" in pack.get("hashes", {})
        dest = Path(d) / "dest"
        unpack = unpack_bundle(out_zip, dest, verify_hashes=True)
        assert unpack.get("verified") is True
        assert (dest / "a.txt").read_text(encoding="utf-8") == "hello"


def test_hash_deterministic() -> None:
    assert hash_content(b"x") == hash_content(b"x")
    assert hash_content(b"x") != hash_content(b"y")