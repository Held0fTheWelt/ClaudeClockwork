from __future__ import annotations

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


def _clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def _decide(complexity: int, risk: int, urgency: int, mode: str) -> tuple[str, str, int]:
    score = (2 * complexity) + (2 * risk) + urgency

    if mode == "cheap":
        if score <= 6:
            return "O1", "C0", 0
        if score <= 10:
            return "O1", "C1", 1
        return "O2", "C1", 2

    if mode == "deep":
        if score <= 6:
            return "O2", "C1", 1
        if score <= 10:
            return "O3", "C2", 2
        return "O3", "C3", 3

    # balanced (default)
    if score <= 6:
        return "O1", "C0", 0
    if score <= 10:
        return "O2", "C1", 1
    if score <= 13:
        return "O2", "C2", 2
    return "O3", "C2", 3


class BudgetRouterSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        complexity = _clamp(int(kwargs.get("complexity", 2)), 0, 5)
        risk = _clamp(int(kwargs.get("risk", 2)), 0, 5)
        urgency = _clamp(int(kwargs.get("urgency", 2)), 0, 5)
        mode = str(kwargs.get("mode", "balanced")).lower()

        tier, model, escalation_level = _decide(complexity, risk, urgency, mode)
        score = (2 * complexity) + (2 * risk) + urgency
        rationale = (
            f"score={score} (complexity={complexity}, risk={risk}, urgency={urgency}), "
            f"mode={mode} → tier={tier}, model={model}"
        )

        return SkillResult(
            True,
            "budget_router",
            data={
                "tier": tier,
                "model": model,
                "rationale": rationale,
                "escalation_level": escalation_level,
            },
        )
