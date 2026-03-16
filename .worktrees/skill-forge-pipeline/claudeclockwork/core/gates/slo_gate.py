"""Phase 39 — SLO gate: failure rate and p95 latency thresholds."""
from __future__ import annotations

from typing import Any, Sequence


def run_slo_gate(
    runs: Sequence[dict[str, Any]],
    max_failure_rate: float = 0.1,
    p95_latency_ms_max: float | None = None,
) -> dict[str, Any]:
    """Check SLO: failure rate and optional p95 latency. Returns {passed, failure_rate, p95_ms}."""
    if not runs:
        return {"passed": True, "failure_rate": 0.0, "p95_ms": None}
    failures = sum(1 for r in runs if r.get("status") == "fail" or r.get("status") == "error")
    rate = failures / len(runs)
    latencies = [r.get("duration_ms") for r in runs if isinstance(r.get("duration_ms"), (int, float))]
    latencies.sort()
    p95_ms = None
    if latencies:
        idx = int(len(latencies) * 0.95) or 0
        p95_ms = latencies[min(idx, len(latencies) - 1)]
    passed = rate <= max_failure_rate
    if p95_latency_ms_max is not None and p95_ms is not None:
        passed = passed and p95_ms <= p95_latency_ms_max
    return {"passed": passed, "failure_rate": rate, "p95_ms": p95_ms}