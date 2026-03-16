"""Phase 41 — Cost/perf regression gate: latency and cost budgets."""
from __future__ import annotations

from typing import Any, Sequence


def run_cost_perf_gate(
    runs: Sequence[dict[str, Any]],
    max_latency_p95_ms: float = 60000,
    max_cost_units: float | None = None,
    budget_profile: str = "balanced",
) -> dict[str, Any]:
    """Gate fails if p95 latency or cost exceeds budget. Returns {passed, p95_ms, cost}."""
    if not runs:
        return {"passed": True, "p95_ms": None, "cost": 0}
    latencies = [r.get("duration_ms") for r in runs if isinstance(r.get("duration_ms"), (int, float))]
    latencies.sort()
    p95_ms = latencies[int(len(latencies) * 0.95)] if latencies else None
    cost = sum(r.get("cost_units", 0) for r in runs)
    passed = True
    if p95_ms is not None and p95_ms > max_latency_p95_ms:
        passed = False
    if max_cost_units is not None and cost > max_cost_units:
        passed = False
    return {"passed": passed, "p95_ms": p95_ms, "cost": cost, "budget_profile": budget_profile}