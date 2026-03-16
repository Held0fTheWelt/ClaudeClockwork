"""Phase 41 — Cost model deterministic."""
from __future__ import annotations

import pytest

from claudeclockwork.optimizer.cost_model import estimate_cost, BUDGET_PROFILES


def test_cost_identical_for_same_inputs() -> None:
    a = estimate_cost("n1", False, 2)
    b = estimate_cost("n1", False, 2)
    assert a == b
    assert "expected_latency_ms" in a
    assert "expected_gpu_minutes" in a