#!/usr/bin/env python3
from __future__ import annotations

"""Deterministic budgeting for routing decisions.

Provider-agnostic: this recommends tiers/constraints only.
"""

from dataclasses import dataclass


def _clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


@dataclass(frozen=True)
class BudgetDecision:
    local_model_tier: str
    claude_tier: str
    allow_deep: bool
    allow_external: bool
    max_context_kb: int


def _decide(complexity: int, risk: int, urgency: int, mode: str) -> BudgetDecision:
    complexity = _clamp(complexity, 0, 5)
    risk = _clamp(risk, 0, 5)
    urgency = _clamp(urgency, 0, 5)
    mode = (mode or "balanced").lower()

    score = (2 * complexity) + (2 * risk) + urgency

    if mode == "cheap":
        if score <= 6:
            return BudgetDecision("O1", "C0", False, False, 64)
        if score <= 10:
            return BudgetDecision("O1", "C1", False, False, 96)
        return BudgetDecision("O2", "C1", False, False, 128)

    if mode == "deep":
        if score <= 6:
            return BudgetDecision("O2", "C1", False, False, 128)
        if score <= 10:
            return BudgetDecision("O3", "C2", True, False, 192)
        return BudgetDecision("O3", "C3", True, True, 256)

    # balanced
    if score <= 6:
        return BudgetDecision("O1", "C0", False, False, 96)
    if score <= 10:
        return BudgetDecision("O2", "C1", False, False, 128)
    if score <= 13:
        return BudgetDecision("O2", "C2", True, False, 192)
    return BudgetDecision("O3", "C2", True, True, 256)


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    d = _decide(
        complexity=int(inputs.get("complexity", 2)),
        risk=int(inputs.get("risk", 2)),
        urgency=int(inputs.get("urgency", 2)),
        mode=str(inputs.get("mode", "balanced")),
    )

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "budget_router"),
        "status": "ok",
        "outputs": {
            "decision": {
                "local_model_tier": d.local_model_tier,
                "claude_tier": d.claude_tier,
                "allow_deep": d.allow_deep,
                "allow_external": d.allow_external,
                "max_context_kb": d.max_context_kb,
            }
        },
        "metrics": {},
        "errors": [],
        "warnings": [],
    }
