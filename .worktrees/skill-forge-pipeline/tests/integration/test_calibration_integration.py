"""Integration: calibration reads telemetry from disk."""
import pytest
from pathlib import Path
from claudeclockwork.optimizer.cost_telemetry import record_cost_event
from claudeclockwork.optimizer.calibration import run_calibration


@pytest.mark.integration
def test_calibration_integration(tmp_path: Path) -> None:
    record_cost_event(tmp_path, "r1", "n1", 1.0, 100.0)
    out = run_calibration(tmp_path)
    assert out["n_events"] == 1
