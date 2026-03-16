"""Phase 42 — Incident summary deterministic."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.cli.incidents import incident_summary


def test_incident_same_telemetry_same_output() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / ".clockwork_runtime" / "telemetry").mkdir(parents=True)
        events = root / ".clockwork_runtime" / "telemetry" / "events.jsonl"
        events.write_text('{"status":"fail","node_id":"n1","error_code":"timeout"}\n')
        a = incident_summary(root)
        b = incident_summary(root)
        assert a == b
        assert a.get("failed_node") == "n1"
        assert "timeout" in a.get("error_codes", [])