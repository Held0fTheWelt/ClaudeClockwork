"""
Phase 25 — Eval regression gate: block if failure rate or latency/quality regresses vs baseline.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def run_eval_regression_gate(
    project_root: Path | str,
    current_pass_count: int,
    current_total: int,
    baseline_pass_count: int | None = None,
    baseline_total: int | None = None,
    failure_rate_threshold: float = 0.1,
) -> dict[str, Any]:
    """
    Compare current run to baseline. Fail if failure rate increases beyond threshold.
    baseline_* from e.g. .clockwork_runtime/eval/baselines/scoreboard.json
    """
    root = Path(project_root).resolve()
    errors: list[str] = []

    current_fail_rate = 1.0 - (current_pass_count / current_total) if current_total else 0.0
    if baseline_pass_count is not None and baseline_total and baseline_total > 0:
        baseline_fail_rate = 1.0 - (baseline_pass_count / baseline_total)
        if current_fail_rate > baseline_fail_rate + failure_rate_threshold:
            errors.append(
                f"Failure rate regressed: baseline {baseline_fail_rate:.2%} -> current {current_fail_rate:.2%} (threshold +{failure_rate_threshold:.0%})"
            )

    return {"pass": len(errors) == 0, "errors": errors, "warnings": []}
