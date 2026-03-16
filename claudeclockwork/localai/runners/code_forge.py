"""Phase 21 — CodeForgeRunner: Adapter for CodeForgeCapability."""
from __future__ import annotations

from typing import Any
from claudeclockwork.localai.runners.base import BaseRunner
from claudeclockwork.localai.capabilities import CodeForgeCapability


class CodeForgeRunner(BaseRunner):
    """Runner adapter for code.forge capability."""

    def __init__(self):
        """Initialize CodeForgeRunner."""
        self._capability = CodeForgeCapability()

    @property
    def capability(self) -> str:
        """Return capability name."""
        return "code.forge"

    def is_available(self) -> bool:
        """Check if capability is available."""
        return self._capability is not None

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Run code.forge capability.

        Args:
            inputs: Request dict

        Returns:
            Contract-shaped result dict
        """
        if not self.is_available():
            return {
                "status": "error",
                "capability": "code.forge",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "dependency_missing", "message": "code.forge not available"}],
            }

        try:
            result = self._capability.forge(inputs)
            return {
                "status": "ok",
                "capability": "code.forge",
                "inputs": inputs,
                "outputs": result,
                "metrics": {},
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "error",
                "capability": "code.forge",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "runtime_error", "message": str(e)}],
            }
