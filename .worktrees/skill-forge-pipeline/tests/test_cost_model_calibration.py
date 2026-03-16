"""Phase 49 — Cost model calibration: telemetry, calibration job, validation, regression gate."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.optimizer.cost_telemetry import record_cost_event, load_cost_events
from claudeclockwork.optimizer.calibration import run_calibration, validate_predictions
from claudeclockwork.core.gates.cost_regression_gate import run_cost_regression_gate


def test_cost_telemetry_record_and_load(tmp_path: Path) -> None:
    record_cost_event(tmp_path, "run1", "node_a", 10.0, 100.0)
    record_cost_event(tmp_path, "run1", "node_b", 20.0, 200.0)
    events = load_cost_events(tmp_path)
    assert len(events) == 2
    assert events[0]["node_id"] == "node_a" and events[0]["cost_units"] == 10.0


def test_calibration_deterministic(tmp_path: Path) -> None:
    record_cost_event(tmp_path, "r1", "n1", 5.0, 50.0)
    record_cost_event(tmp_path, "r1", "n1", 7.0, 70.0)
    out = run_calibration(tmp_path)
    assert out["n_events"] == 2
    assert "n1" in out["calibrated"]
    assert out["calibrated"]["n1"]["mean_cost"] == 6.0
    assert out["calibrated"]["n1"]["mean_duration_ms"] == 60.0


def test_validate_predictions(tmp_path: Path) -> None:
    record_cost_event(tmp_path, "r1", "n1", 1.0, 100.0)
    out = validate_predictions(tmp_path)
    assert "mae" in out and "passed" in out


def test_cost_regression_gate_passes(tmp_path: Path) -> None:
    record_cost_event(tmp_path, "run1", "n1", 10.0, 100.0)
    result = run_cost_regression_gate(tmp_path, max_total_cost=100.0)
    assert result["passed"] is True
    assert result["last_run_cost"] == 10.0


def test_cost_regression_gate_fails(tmp_path: Path) -> None:
    record_cost_event(tmp_path, "run1", "n1", 500.0, 100.0)
    result = run_cost_regression_gate(tmp_path, max_total_cost=100.0)
    assert result["passed"] is False
    assert result["last_run_cost"] == 500.0
