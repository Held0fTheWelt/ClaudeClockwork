"""Phase 27 — Adapter batch plan and rollback tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_adapter_batch_plan_deterministic() -> None:
    """Same repo state produces same batch list."""
    root = Path(__file__).resolve().parents[1]
    r1 = subprocess.run(
        [sys.executable, "scripts/adapter_batch_plan.py", "--batch-size", "10"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert r1.returncode == 0
    batch1 = json.loads(r1.stdout)
    r2 = subprocess.run(
        [sys.executable, "scripts/adapter_batch_plan.py", "--batch-size", "10"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert r2.returncode == 0
    batch2 = json.loads(r2.stdout)
    assert batch1 == batch2


def test_adapter_batch_run_dry_run_exits_zero() -> None:
    """Dry run does not convert, exits 0."""
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run(
        [sys.executable, "scripts/adapter_batch_run.py", "--dry-run"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0


def test_snapshot_create_and_restore() -> None:
    """Snapshot create and restore round-trip."""
    import tempfile
    from claudeclockwork.core.snapshot import create_snapshot, restore_snapshot

    with tempfile.TemporaryDirectory() as project:
        with tempfile.TemporaryDirectory() as snap_dir:
            project_p = Path(project)
            (project_p / "foo").mkdir(parents=True)
            (project_p / "foo" / "f.txt").write_text("hello", encoding="utf-8")
            create_snapshot(project_p, ["foo/f.txt"], snap_dir)
            (project_p / "foo" / "f.txt").write_text("changed", encoding="utf-8")
            restore_snapshot(project_p, snap_dir)
            assert (project_p / "foo" / "f.txt").read_text() == "hello"
