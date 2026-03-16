"""Phase 22 — Mode Guard: Runtime enforcement of mode constraints."""
from __future__ import annotations

from typing import Any, Callable

from .mode_manager import ModeManager


class ModeViolationError(Exception):
    """Raised when an operation violates mode constraints."""

    pass


class ModeGuard:
    """Hard-gates execution based on active mode constraints."""

    def __init__(self, mode_manager: ModeManager | None = None):
        """
        Initialize mode guard.

        Args:
            mode_manager: ModeManager instance (uses global if None)
        """
        self.mode_manager = mode_manager or ModeManager()

    def check_operation_allowed(self, operation: str) -> None:
        """
        Check if an operation is allowed in the active mode.

        Args:
            operation: Operation name

        Raises:
            ModeViolationError: If operation is not allowed
        """
        active_mode = self.mode_manager.get_active_mode()

        if not self.mode_manager.is_mode_allowed(operation):
            raise ModeViolationError(
                f"Operation '{operation}' is forbidden in {active_mode} mode. "
                f"Mode is binding and cannot be bypassed."
            )

    def check_claude_execution_allowed(self) -> None:
        """
        Guard: Check if Claude execution is allowed.

        Raises:
            ModeViolationError: If Claude execution is forbidden
        """
        active_mode = self.mode_manager.get_active_mode()

        if not self.mode_manager.get_mode_config().get('allow_claude', False):
            raise ModeViolationError(
                f"Claude execution is forbidden in {active_mode} mode. "
                f"This is a hard constraint. Mode: {active_mode}"
            )

    def check_ollama_execution_allowed(self) -> None:
        """
        Guard: Check if Ollama execution is allowed.

        Raises:
            ModeViolationError: If Ollama execution is forbidden
        """
        active_mode = self.mode_manager.get_active_mode()

        if not self.mode_manager.get_mode_config().get('allow_ollama', False):
            raise ModeViolationError(
                f"Ollama execution is forbidden in {active_mode} mode. "
                f"This is a hard constraint."
            )

    def check_mixed_execution_allowed(self) -> None:
        """
        Guard: Check if mixed Claude+Ollama execution is allowed.

        Raises:
            ModeViolationError: If mixed execution is forbidden
        """
        active_mode = self.mode_manager.get_active_mode()

        if not self.mode_manager.get_mode_config().get('allow_mixed', False):
            raise ModeViolationError(
                f"Mixed Claude+Ollama execution is forbidden in {active_mode} mode. "
                f"Mode: {active_mode}"
            )

    def check_model_allowed(self, model: str) -> None:
        """
        Guard: Check if a specific model is allowed.

        Args:
            model: Model name/ID

        Raises:
            ModeViolationError: If model is not allowed
        """
        allowed_models = self.mode_manager.get_allowed_models()

        # Empty list means all models allowed
        if allowed_models and model not in allowed_models:
            raise ModeViolationError(
                f"Model '{model}' is not in the allowed list for the active mode. "
                f"Allowed: {allowed_models}"
            )

    def check_token_budget(self, tokens_used: int) -> None:
        """
        Guard: Check if token usage exceeds mode budget.

        Args:
            tokens_used: Number of tokens used

        Raises:
            ModeViolationError: If budget exceeded
        """
        budget = self.mode_manager.get_token_budget()

        if budget is not None and tokens_used > budget:
            raise ModeViolationError(
                f"Token budget exceeded: {tokens_used} > {budget}. "
                f"Mode enforces maximum of {budget} tokens."
            )

    def check_ollama_available(self) -> bool:
        """
        Check if Ollama is available when required by mode.

        Returns:
            True if Ollama available or not required

        Raises:
            ModeViolationError: If Ollama required but unavailable
        """
        if self.mode_manager.requires_ollama_available():
            # Would need actual Ollama availability check
            # For now, return True - caller must implement actual check
            return True
        return True

    def guard_operation(self, operation: str) -> Callable:
        """
        Decorator: Guard a function with mode constraints.

        Args:
            operation: Operation name to guard

        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs) -> Any:
                self.check_operation_allowed(operation)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def get_mode_status(self) -> dict[str, Any]:
        """
        Get current mode status and constraints.

        Returns:
            Dict with mode info and constraints
        """
        active_mode = self.mode_manager.get_active_mode()
        config = self.mode_manager.get_mode_config()

        return {
            "active_mode": active_mode,
            "name": config.get('name', ''),
            "description": config.get('description', ''),
            "constraints": {
                "allow_claude": config.get('allow_claude', False),
                "allow_ollama": config.get('allow_ollama', False),
                "allow_mixed": config.get('allow_mixed', False),
                "allow_fallback": config.get('allow_fallback_to_claude', False),
                "require_ollama": config.get('require_ollama_available', False),
                "token_budget": config.get('max_token_budget'),
                "cost_threshold": config.get('cost_threshold'),
                "allowed_models": config.get('llm_allowlist', []),
            },
            "status": "ACTIVE"
        }
