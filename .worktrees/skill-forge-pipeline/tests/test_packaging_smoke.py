"""Phase 28 — Packaging smoke: build and minimal CLI (no full pytest)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_cli_help_exits_zero() -> None:
    """CLI --help runs and exits 0."""
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli", "--help"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert "ClaudeClockwork" in r.stdout or "skill-id" in r.stdout


def test_first_run_subcommand_exists() -> None:
    """first-run subcommand exists."""
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli", "--project-root", str(root), "first-run"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert "runtime_root" in r.stdout or "ok" in r.stdout
