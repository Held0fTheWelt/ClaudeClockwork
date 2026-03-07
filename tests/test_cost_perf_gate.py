"""Phase 41 — Cost/perf gate."""
from __future__ import annotations

import pytest

from claudeclockwork.core.gates.cost_perf_gate import run_cost_perf_gate


def test_gate_passes_under_budget() -> None:
    out = run_cost_perf_gate([{"duration_ms": 100}], max_latency_p95_ms=1000)
    assert out["passed"] is True