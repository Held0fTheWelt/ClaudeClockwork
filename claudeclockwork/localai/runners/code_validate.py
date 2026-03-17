"""Phase 21 — CodeValidateRunner: Adapter for CodeValidateCapability."""
from __future__ import annotations

from typing import Any
from claudeclockwork.localai.runners.base import BaseRunner
from claudeclockwork.localai.capabilities import CodeValidateCapability


class CodeValidateRunner(BaseRunner):
    """Runner adapter for code.validate capability."""

    def __init__(self):
        """Initialize CodeValidateRunner."""
        self._capability = CodeValidateCapability()

    @property
    def capability(self) -> str:
        """Return capability name."""
        return "code.validate"

    def is_available(self) -> bool:
        """Check if capability is available."""
        return self._capability is not None

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Run code.validate capability.

        Args:
            inputs: Dict with keys: code, archetype

        Returns:
            Contract-shaped result dict
        """
        if not self.is_available():
            return {
                "status": "error",
                "capability": "code.validate",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "dependency_missing", "message": "code.validate not available"}],
            }

        try:
            code = inputs.get("code", "")
            archetype = inputs.get("archetype", "transformer")

            result = self._capability.validate(code, archetype)
            return {
                "status": "ok",
                "capability": "code.validate",
                "inputs": inputs,
                "outputs": result,
                "metrics": {},
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "error",
                "capability": "code.validate",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "runtime_error", "message": str(e)}],
            }
