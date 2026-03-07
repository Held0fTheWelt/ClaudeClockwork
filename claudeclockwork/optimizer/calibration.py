"""Phase 49 — Offline calibration job: fit simple predictor from cost telemetry. Deterministic."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.optimizer.cost_telemetry import load_cost_events
from claudeclockwork.optimizer.cost_model import estimate_cost


def run_calibration(run_root: Path | str) -> dict[str, Any]:
    """
    Load cost events, fit simple predictor (mean cost_units per node_id, mean duration per node_id).
    Returns { "calibrated": { node_id: { "mean_cost": float, "mean_duration_ms": float } }, "n_events": int }.
    Deterministic.
    """
    events = load_cost_events(run_root)
    by_node: dict[str, list[dict[str, Any]]] = {}
    for e in events:
        nid = e.get("node_id") or "default"
        by_node.setdefault(nid, []).append(e)
    calibrated: dict[str, dict[str, float]] = {}
    for nid, evs in sorted(by_node.items()):
        costs = [x.get("cost_units", 0) for x in evs if isinstance(x.get("cost_units"), (int, float))]
        durs = [x.get("duration_ms", 0) for x in evs if isinstance(x.get("duration_ms"), (int, float))]
        calibrated[nid] = {
            "mean_cost": sum(costs) / len(costs) if costs else 0.0,
            "mean_duration_ms": sum(durs) / len(durs) if durs else 0.0,
        }
    return {"calibrated": calibrated, "n_events": len(events)}


def validate_predictions(run_root: Path | str) -> dict[str, Any]:
    """Compare predicted (estimate_cost) vs observed (calibration means). Returns mae and pass threshold."""
    cal = run_calibration(run_root)
    errors = []
    for nid, obs in cal["calibrated"].items():
        pred = estimate_cost(node_id=nid, has_gpu=False, input_refs=0)
        pred_cost = pred.get("expected_latency_ms", 0) / 1000.0  # use as proxy cost for comparison
        obs_cost = obs.get("mean_cost", 0)
        errors.append(abs(pred_cost - obs_cost))
    mae = sum(errors) / len(errors) if errors else 0.0
    return {"mae": mae, "n_nodes": len(cal["calibrated"]), "passed": mae < 100.0}
