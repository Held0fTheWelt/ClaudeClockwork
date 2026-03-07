"""
Phase 46 — CI smoke: run at least one demo pipeline end-to-end.

Deterministic; uses stubbed work graph runner.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMOKE_GRAPH = ROOT / "demos" / "smoke" / "graph.json"


def test_demo_smoke_runs_e2e() -> None:
    """Run smoke demo graph; assert status ok (CI smoke mode)."""
    assert SMOKE_GRAPH.is_file(), "demos/smoke/graph.json must exist"
    proc = subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli.run_graph", str(SMOKE_GRAPH), "--project-root", str(ROOT)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, f"Demo failed: {proc.stderr or proc.stdout}"
    data = json.loads(proc.stdout)
    assert data.get("status") == "ok", data
    assert "results" in data
    assert "gate" in data["results"] and "step" in data["results"]
