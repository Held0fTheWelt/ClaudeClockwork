"""Phase 39 — Work graph rollback: snapshot + restore on failure."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.workgraph.snapshot import snapshot_before_graph, restore_on_failure


def test_rollback_restores_state() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        run_root = root / ".clockwork_runtime"
        run_root.mkdir(parents=True)
        cache_dir = run_root / "workgraph_cache"
        cache_dir.mkdir(parents=True)
        (cache_dir / "old.json").write_text("before")
        snap = snapshot_before_graph(root)
        (cache_dir / "old.json").write_text("after")
        restore_on_failure(root, snap)
        assert (cache_dir / "old.json").read_text() == "before"
        assert (run_root / "rollback_evidence.jsonl").exists()