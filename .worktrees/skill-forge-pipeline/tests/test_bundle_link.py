"""Phase 43 — Bundle link: no paths outside project boundary."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.workspace.bundle_link import link_bundle


def test_link_bundle_under_project_runtime() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        bundle_dir = root / "bundle_dir"
        bundle_dir.mkdir()
        (bundle_dir / "x.txt").write_text("data")
        out = link_bundle(root, bundle_dir, bundle_id="b1", version="1")
        assert out.get("bundle_id") == "b1"
        assert (root / ".clockwork_runtime" / "bundle_links.jsonl").exists()