"""Phase 26 — Router v3 output contract: chosen option, rationale, reason codes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def extract_task_features(task_type: str, input_size: int = 0, modality: str = "text") -> dict[str, Any]:
    """Feature extraction for router: task size, modality, risk (Phase 26)."""
    risk = "low"
    if "security" in task_type or "redact" in task_type:
        risk = "high"
    elif "eval" in task_type or "gate" in task_type:
        risk = "medium"
    return {
        "task_size": min(3, input_size // 1000) if input_size else 0,
        "modality": modality,
        "risk": risk,
    }


@dataclass
class RouterRationale:
    """Explainable router decision (Phase 26 contract)."""
    chosen_option: str
    alternatives_considered: list[str]
    reason_codes: list[str]  # budget, latency, quality, safety
    confidence: float | None
    expected_cost: float | None
    budget_level: str  # fast | balanced | strong


def select_with_rationale(
    options: list[str],
    budget_level: str,
    features: dict[str, Any] | None = None,
    seed: int | None = None,
) -> RouterRationale:
    """
    Deterministic selection with rationale. When seed is set, choice is reproducible.
    Budget level affects which options are preferred (fast -> first cheap, strong -> last).
    """
    features = features or {}
    # Simple deterministic rule: budget picks index into options (fast=0, balanced=mid, strong=last)
    n = len(options)
    if n == 0:
        return RouterRationale(
            chosen_option="",
            alternatives_considered=[],
            reason_codes=["no_options"],
            confidence=None,
            expected_cost=None,
            budget_level=budget_level,
        )
    if budget_level == "fast":
        idx = 0
        reason_codes = ["budget", "latency"]
    elif budget_level == "strong":
        idx = n - 1
        reason_codes = ["budget", "quality"]
    else:
        idx = n // 2
        reason_codes = ["budget", "balanced"]
    chosen = options[idx]
    return RouterRationale(
        chosen_option=chosen,
        alternatives_considered=options,
        reason_codes=reason_codes,
        confidence=0.9,
        expected_cost=None,
        budget_level=budget_level,
    )
