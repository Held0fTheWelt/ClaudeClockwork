"""Phase 50 — Smart caching: pinning, reuse, poisoning rejection."""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.cas.store import put, get
from claudeclockwork.cas.smart_cache import (
    pin,
    get_pinned,
    put_with_provenance,
    get_safe,
)


def test_pinning_exists(tmp_path: Path) -> None:
    pin(tmp_path, "abc123")
    pin(tmp_path, "def456")
    assert get_pinned(tmp_path) == {"abc123", "def456"}


def test_reuse_only_when_pinned(tmp_path: Path) -> None:
    h = put(tmp_path, b"data", metadata={})
    assert get(tmp_path, h) == b"data"
    assert get_safe(tmp_path, h, require_pinned=True) is None
    pin(tmp_path, h)
    assert get_safe(tmp_path, h, require_pinned=True) == b"data"


def test_poisoning_rejection(tmp_path: Path) -> None:
    h = put_with_provenance(tmp_path, b"data", source_bundle_id="bundle_a", project_id="p1")
    pin(tmp_path, h)
    assert get_safe(tmp_path, h, allowed_bundles=set(), require_pinned=True) is None
    assert get_safe(tmp_path, h, allowed_bundles={"bundle_a"}, require_pinned=True) == b"data"
