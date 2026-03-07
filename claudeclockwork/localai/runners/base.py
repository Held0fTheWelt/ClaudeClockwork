"""Phase 20 — Base runner interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseRunner(ABC):
    """Runner for a local capability. Returns contract-shaped dict or dependency_missing error."""

    @property
    @abstractmethod
    def capability(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """True if the runner can execute (deps installed)."""
        raise NotImplementedError

    @abstractmethod
    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Execute and return local_tool_result-shaped dict.
        If not available, return status=error with errors=[{code: "dependency_missing", ...}].
        """
        raise NotImplementedError
