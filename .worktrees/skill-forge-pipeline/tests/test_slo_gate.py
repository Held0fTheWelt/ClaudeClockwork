"""Phase 39 — SLO gate tests."""
from __future__ import annotations

import pytest

from claudeclockwork.core.gates.slo_gate import run_slo_gate


def test_slo_passes_under_threshold() -> None:
    runs = [{"status": "ok"}, {"status": "ok"}, {"status": "fail"}]
    out = run_slo_gate(runs, max_failure_rate=0.5)
    assert out["passed"] is True
    assert out["failure_rate"] == 1 / 3


def test_slo_fails_over_threshold() -> None:
    runs = [{"status": "ok"}, {"status": "fail"}, {"status": "fail"}]
    out = run_slo_gate(runs, max_failure_rate=0.3)
    assert out["passed"] is False