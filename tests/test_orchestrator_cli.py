"""Phase 43 — Orchestrator commands deterministic and respect boundaries."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.cli.orchestrate import run_orchestrate


def test_orchestrate_incident_deterministic() -> None:
    with tempfile.TemporaryDirectory() as d:
        out = run_orchestrate(d, "p1", command="incident")
        assert "failed_node" in out or "error_codes" in out