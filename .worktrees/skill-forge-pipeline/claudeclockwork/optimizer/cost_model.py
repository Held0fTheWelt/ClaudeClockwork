"""Phase 41 — Cost model: latency, GPU minutes, memory, failure risk. Deterministic."""
from __future__ import annotations

from typing import Any


def estimate_cost(
    node_id: str = "",
    has_gpu: bool = False,
    input_refs: int = 0,
) -> dict[str, Any]:
    """Deterministic cost estimate. Same inputs → identical output."""
    latency_ms = 100 + len(node_id) * 10 + input_refs * 5
    gpu_minutes = 0.1 if has_gpu else 0.0
    memory_mb = 256 + input_refs * 16
    risk = 0.05 if input_refs > 5 else 0.02
    return {
        "expected_latency_ms": latency_ms,
        "expected_gpu_minutes": gpu_minutes,
        "expected_memory_mb": memory_mb,
        "expected_failure_risk": risk,
    }


BUDGET_PROFILES = {
    "fast": {"max_latency_ms": 5000, "max_gpu_minutes": 0},
    "balanced": {"max_latency_ms": 30000, "max_gpu_minutes": 10},
    "strong": {"max_latency_ms": 120000, "max_gpu_minutes": 60},
}