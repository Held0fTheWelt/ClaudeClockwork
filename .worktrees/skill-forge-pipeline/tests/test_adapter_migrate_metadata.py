"""Phase 21 — Adapter migrate metadata normalization and check."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_adapter_migrate_check_metadata_exit_zero() -> None:
    """check-metadata exits 0 when all manifests have legacy_bridge."""
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run(
        [sys.executable, "scripts/adapter_migrate.py", "check-metadata"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "metadata.legacy_bridge" in r.stdout or "All manifests" in r.stdout


def test_adapter_migrate_normalize_metadata_idempotent() -> None:
    """normalize-metadata is idempotent (second run changes nothing)."""
    root = Path(__file__).resolve().parents[1]
    r1 = subprocess.run(
        [sys.executable, "scripts/adapter_migrate.py", "normalize-metadata"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert r1.returncode == 0
    r2 = subprocess.run(
        [sys.executable, "scripts/adapter_migrate.py", "normalize-metadata"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert r2.returncode == 0
    # Second run should report no updates (or "All manifests already have")
    assert "Updated 0" in r2.stdout or "already have" in r2.stdout
