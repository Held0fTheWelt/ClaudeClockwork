"""Phase 32 — Telemetry summary and parsing tests."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from claudeclockwork.cli.telemetry_summary import run_telemetry_summary
from claudeclockwork.telemetry.writer import write_event


def test_telemetry_summary_deterministic() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "telemetry").mkdir(parents=True)
        (root / "telemetry" / "events.jsonl").write_text(
            '{"run_id":"r1","node_id":"n1","status":"ok","duration_ms":10}\n'
            '{"run_id":"r2","node_id":"n1","status":"fail","error_codes":["timeout"]}\n',
            encoding="utf-8",
        )
        s1 = run_telemetry_summary(root, last_n=20)
        s2 = run_telemetry_summary(root, last_n=20)
        assert s1 == s2
        assert s1["failure_count"] == 1
        assert any(c[0] == "timeout" for c in s1["top_error_codes"])


def test_telemetry_writer_append_event() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        write_event(root, run_id="r1", node_id="n1", capability="skill_x", status="ok")
        path = root / "telemetry" / "events.jsonl"
        assert path.is_file()
        line = path.read_text().strip()
        data = json.loads(line)
        assert data["run_id"] == "r1" and data["status"] == "ok"
