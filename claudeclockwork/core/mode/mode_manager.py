"""Phase 22 — Mode Manager: Persistent execution mode state and lifecycle."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class ModeManager:
    """Manages execution mode state and configuration."""

    # Standard mode state file location
    STATE_FILE = Path(".claude") / "state" / "mode_state.json"

    # Canonical mode profiles
    PROFILES_FILE = Path(".claude") / "config" / "mode_profiles.yaml"

    def __init__(self):
        """Initialize mode manager."""
        self._profiles = None
        self._active_mode = None
        self._load_profiles()
        self._load_active_mode()

    def _load_profiles(self) -> None:
        """Load canonical mode profiles from config."""
        try:
            with open(self.PROFILES_FILE, 'r') as f:
                config = yaml.safe_load(f)
            self._profiles = config.get('modes', {})
            self._default_mode = config.get('default_mode', 'default')
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise RuntimeError(f"Failed to load mode profiles: {e}")

    def _load_active_mode(self) -> None:
        """Load currently active mode from state file."""
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, 'r') as f:
                    state = json.load(f)
                self._active_mode = state.get('active_mode')
                if self._active_mode and self._active_mode not in self._profiles:
                    raise ValueError(f"Invalid mode in state file: {self._active_mode}")
            except (json.JSONDecodeError, ValueError) as e:
                raise RuntimeError(f"Failed to load mode state: {e}")
        else:
            # Initialize with default mode
            self._active_mode = self._default_mode
            self._save_state()

    def _save_state(self) -> None:
        """Persist active mode to state file."""
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "active_mode": self._active_mode,
            "last_updated": datetime.now().isoformat(),
            "last_updated_by": "mode_manager"
        }
        with open(self.STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)

    def get_active_mode(self) -> str:
        """Get the currently active mode name."""
        return self._active_mode

    def get_mode_config(self, mode_name: str | None = None) -> dict[str, Any]:
        """
        Get configuration for a mode.

        Args:
            mode_name: Mode name. If None, returns active mode config.

        Returns:
            Mode configuration dictionary
        """
        if mode_name is None:
            mode_name = self._active_mode

        if mode_name not in self._profiles:
            raise ValueError(f"Unknown mode: {mode_name}")

        return self._profiles[mode_name]

    def set_mode(self, mode_name: str) -> None:
        """
        Set the active execution mode.

        Args:
            mode_name: Name of the mode to activate

        Raises:
            ValueError: If mode is invalid or transition not allowed
        """
        if mode_name not in self._profiles:
            raise ValueError(f"Unknown mode: {mode_name}")

        # Verify transition is allowed
        if self._active_mode != mode_name:
            transition_rules = self._load_transition_rules()
            if mode_name not in transition_rules.get(self._active_mode, []):
                raise ValueError(
                    f"Cannot transition from {self._active_mode} to {mode_name}"
                )

        self._active_mode = mode_name
        self._save_state()

    def list_modes(self) -> dict[str, str]:
        """
        List all available modes with descriptions.

        Returns:
            Dict mapping mode names to descriptions
        """
        return {
            name: config.get('description', '')
            for name, config in self._profiles.items()
        }

    def validate_mode(self, mode_name: str) -> tuple[bool, str]:
        """
        Validate if a mode name is valid.

        Args:
            mode_name: Mode name to validate

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        if mode_name in self._profiles:
            return True, f"Mode '{mode_name}' is valid"
        return False, f"Mode '{mode_name}' not found"

    def _load_transition_rules(self) -> dict[str, list[str]]:
        """Load mode transition rules from profiles."""
        try:
            with open(self.PROFILES_FILE, 'r') as f:
                config = yaml.safe_load(f)
            rules = config.get('transition_rules', {})
            # Default: allow all transitions if not specified
            all_modes = list(self._profiles.keys())
            return {
                mode: rules.get(f'from_{mode}_to', all_modes)
                for mode in all_modes
            }
        except Exception:
            # Fallback: allow all transitions
            return {mode: list(self._profiles.keys()) for mode in self._profiles}

    def is_mode_allowed(self, operation: str) -> bool:
        """
        Check if an operation is allowed in the active mode.

        Args:
            operation: Operation name (e.g., 'claude_execution', 'ollama_execution')

        Returns:
            True if operation is allowed in active mode
        """
        mode_config = self.get_mode_config()
        forbidden = self._get_forbidden_operations()

        if self._active_mode in forbidden:
            if operation in forbidden[self._active_mode]:
                return False

        # Explicit allow/deny checks
        if operation == "claude_execution":
            return mode_config.get('allow_claude', False)
        elif operation == "ollama_execution":
            return mode_config.get('allow_ollama', False)
        elif operation == "mixed_execution":
            return mode_config.get('allow_mixed', False)
        elif operation == "claude_fallback":
            return mode_config.get('allow_fallback_to_claude', False)

        return True

    def _get_forbidden_operations(self) -> dict[str, list[str]]:
        """Get forbidden operations by mode from profiles."""
        try:
            with open(self.PROFILES_FILE, 'r') as f:
                config = yaml.safe_load(f)
            return config.get('forbidden_combinations', {})
        except Exception:
            return {}

    def get_cost_threshold(self) -> float | None:
        """Get cost threshold for the active mode."""
        return self.get_mode_config().get('cost_threshold')

    def get_token_budget(self) -> int | None:
        """Get maximum token budget for the active mode."""
        return self.get_mode_config().get('max_token_budget')

    def get_allowed_models(self) -> list[str]:
        """Get list of allowed LLM models for the active mode."""
        return self.get_mode_config().get('llm_allowlist', [])

    def requires_ollama_available(self) -> bool:
        """Check if active mode requires Ollama to be available."""
        return self.get_mode_config().get('require_ollama_available', False)
