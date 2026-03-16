"""Phase 40 — Plugin signing / hash allowlist."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.plugins.signing import content_hash_plugin, load_allowlist, is_allowlisted


def test_hash_deterministic() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "plugin.json").write_text('{"id":"p1"}')
        h1 = content_hash_plugin(root)
        h2 = content_hash_plugin(root)
        assert h1 == h2


def test_strict_rejects_unallowlisted() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "plugins" / "x").mkdir(parents=True)
        (root / "plugins" / "x" / "plugin.json").write_text("{}")
        allowed, reason = is_allowlisted("x", root / "plugins" / "x", root, strict=True)
        assert not allowed
        assert "allowlist" in reason