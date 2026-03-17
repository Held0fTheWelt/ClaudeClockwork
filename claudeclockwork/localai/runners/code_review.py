"""Phase 21 — CodeReviewRunner: Adapter for CodeReviewCapability."""
from __future__ import annotations

from typing import Any
from claudeclockwork.localai.runners.base import BaseRunner
from claudeclockwork.localai.capabilities import CodeReviewCapability


class CodeReviewRunner(BaseRunner):
    """Runner adapter for code.review capability."""

    def __init__(self):
        """Initialize CodeReviewRunner."""
        self._capability = CodeReviewCapability()

    @property
    def capability(self) -> str:
        """Return capability name."""
        return "code.review"

    def is_available(self) -> bool:
        """Check if capability is available."""
        return self._capability is not None

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Run code.review capability.

        Args:
            inputs: Dict with keys: code, archetype

        Returns:
            Contract-shaped result dict
        """
        if not self.is_available():
            return {
                "status": "error",
                "capability": "code.review",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "dependency_missing", "message": "code.review not available"}],
            }

        try:
            code = inputs.get("code", "")
            archetype = inputs.get("archetype", "transformer")

            result = self._capability.review(code, archetype)
            return {
                "status": "ok",
                "capability": "code.review",
                "inputs": inputs,
                "outputs": result,
                "metrics": {},
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "error",
                "capability": "code.review",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "runtime_error", "message": str(e)}],
            }
