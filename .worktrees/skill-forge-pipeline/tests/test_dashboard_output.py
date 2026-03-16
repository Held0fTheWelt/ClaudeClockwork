"""Phase 42 — Dashboard output stable order."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.cli.dashboard import run_dashboard


def test_dashboard_stable_ordering() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / ".clockwork_runtime" / "telemetry").mkdir(parents=True)
        (root / ".clockwork_runtime" / "telemetry" / "events.jsonl").write_text(
            '{"run_id":"r1","timestamp":"2020-01-01T00:00:00"}\n{"run_id":"r2","timestamp":"2020-01-01T00:00:00"}\n'
        )
        out = run_dashboard(root, last_n=5)
        assert "last_runs" in out
        assert sorted(out["last_runs"], key=lambda x: (x.get("timestamp"), x.get("run_id"))) == out["last_runs"]