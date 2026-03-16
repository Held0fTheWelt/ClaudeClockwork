"""Phase 21 — CodePlanRunner: Adapter for CodePlanCapability."""
from __future__ import annotations

from typing import Any
from claudeclockwork.localai.runners.base import BaseRunner
from claudeclockwork.localai.capabilities import CodePlanCapability


class CodePlanRunner(BaseRunner):
    """Runner adapter for code.plan capability."""

    def __init__(self):
        """Initialize CodePlanRunner."""
        self._capability = CodePlanCapability()

    @property
    def capability(self) -> str:
        """Return capability name."""
        return "code.plan"

    def is_available(self) -> bool:
        """Check if capability is available."""
        return self._capability is not None

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Run code.plan capability.

        Args:
            inputs: Dict with task_id, archetype, purpose, constraints

        Returns:
            Contract-shaped result dict
        """
        if not self.is_available():
            return {
                "status": "error",
                "capability": "code.plan",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "dependency_missing", "message": "code.plan not available"}],
            }

        try:
            if not inputs.get("task_id") or not inputs.get("archetype") or not inputs.get("purpose"):
                return {
                    "status": "error",
                    "capability": "code.plan",
                    "inputs": inputs,
                    "outputs": {},
                    "metrics": {},
                    "errors": [{"code": "missing_input", "message": "task_id, archetype, purpose required"}],
                }

            plan_result = self._capability.plan(inputs)

            return {
                "status": "ok",
                "capability": "code.plan",
                "inputs": inputs,
                "outputs": plan_result,
                "metrics": {},
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "error",
                "capability": "code.plan",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "runtime_error", "message": str(e)}],
            }
