"""Phase 55 — Operator toolkit: ops commands deterministic."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ops(cmd: str) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli", "--project-root", str(ROOT), "ops", cmd],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return json.loads(proc.stdout)


def test_ops_bundles() -> None:
    out = _ops("bundles")
    assert "bundles" in out and "count" in out


def test_ops_plugins() -> None:
    out = _ops("plugins")
    assert "plugins" in out and "count" in out


def test_ops_budget() -> None:
    out = _ops("budget")
    assert "budget_profile" in out


def test_ops_cache() -> None:
    out = _ops("cache")
    assert "cas_objects" in out


def test_ops_tui_stub() -> None:
    out = _ops("tui")
    assert out.get("tui") == "optional"
