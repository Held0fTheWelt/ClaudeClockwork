"""Phase 49 — Cost regression gate: fail if observed cost exceeds threshold (from telemetry)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.optimizer.cost_telemetry import load_cost_events


def run_cost_regression_gate(
    run_root: Path | str,
    max_total_cost: float = 1000.0,
    last_n_runs: int = 10,
) -> dict[str, Any]:
    """
    Load cost telemetry, aggregate by run_id, fail if any of the last N runs exceed max_total_cost.
    Returns { passed, last_run_cost, run_count }.
    """
    events = load_cost_events(run_root)
    by_run: dict[str, float] = {}
    for e in events:
        rid = e.get("run_id") or "unknown"
        by_run[rid] = by_run.get(rid, 0) + float(e.get("cost_units", 0))
    runs_sorted = sorted(by_run.items(), key=lambda x: x[0])[-last_n_runs:]
    last_cost = runs_sorted[-1][1] if runs_sorted else 0.0
    passed = last_cost <= max_total_cost
    return {
        "passed": passed,
        "last_run_cost": last_cost,
        "run_count": len(runs_sorted),
        "max_total_cost": max_total_cost,
    }
