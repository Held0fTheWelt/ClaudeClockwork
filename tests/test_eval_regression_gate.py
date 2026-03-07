"""Phase 25 — Eval regression gate tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.core.gates.eval_regression_gate import run_eval_regression_gate


def test_eval_regression_gate_pass_when_no_baseline() -> None:
    """With no baseline, gate passes (no regression to compare)."""
    root = Path(__file__).resolve().parents[1]
    r = run_eval_regression_gate(root, current_pass_count=5, current_total=5)
    assert r["pass"] is True
    assert not r["errors"]


def test_eval_regression_gate_fail_when_failure_rate_increases() -> None:
    """When current failure rate exceeds baseline + threshold, gate fails."""
    root = Path(__file__).resolve().parents[1]
    r = run_eval_regression_gate(
        root,
        current_pass_count=4,
        current_total=10,
        baseline_pass_count=9,
        baseline_total=10,
        failure_rate_threshold=0.1,
    )
    assert r["pass"] is False
    assert any("regressed" in e.lower() for e in r["errors"])


def test_eval_regression_gate_pass_when_improved() -> None:
    """When current is better than baseline, gate passes."""
    root = Path(__file__).resolve().parents[1]
    r = run_eval_regression_gate(
        root,
        current_pass_count=10,
        current_total=10,
        baseline_pass_count=8,
        baseline_total=10,
    )
    assert r["pass"] is True
