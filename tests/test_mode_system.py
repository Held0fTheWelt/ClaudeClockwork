"""Tests for the Mode System (Phase 22)."""
import json
import pytest
from pathlib import Path
from claudeclockwork.core.mode import ModeManager, ModeGuard, ModeViolationError


class TestModeManager:
    """Tests for ModeManager."""

    def test_mode_manager_loads_profiles(self):
        """Test mode manager loads canonical profiles."""
        manager = ModeManager()
        modes = manager.list_modes()
        assert "default" in modes
        assert "adaptive" in modes
        assert "claude-min" in modes

    def test_get_active_mode(self):
        """Test getting the active mode."""
        manager = ModeManager()
        mode = manager.get_active_mode()
        assert mode in ["default", "adaptive", "claude-min"]

    def test_get_mode_config(self):
        """Test getting configuration for a mode."""
        manager = ModeManager()
        config = manager.get_mode_config("default")
        assert "allow_claude" in config
        assert "allow_ollama" in config
        assert "allow_mixed" in config

    def test_get_active_mode_config(self):
        """Test getting config for active mode without specifying name."""
        manager = ModeManager()
        config = manager.get_mode_config()
        assert "allow_claude" in config

    def test_set_mode_valid(self):
        """Test setting mode to a valid mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            # Set to a different mode
            new_mode = "adaptive" if original != "adaptive" else "claude-min"
            manager.set_mode(new_mode)
            assert manager.get_active_mode() == new_mode
        finally:
            # Restore original mode
            manager.set_mode(original)

    def test_set_mode_invalid(self):
        """Test setting mode to invalid mode raises error."""
        manager = ModeManager()
        with pytest.raises(ValueError):
            manager.set_mode("invalid_mode")

    def test_validate_mode_valid(self):
        """Test validating a valid mode."""
        manager = ModeManager()
        is_valid, msg = manager.validate_mode("default")
        assert is_valid is True

    def test_validate_mode_invalid(self):
        """Test validating an invalid mode."""
        manager = ModeManager()
        is_valid, msg = manager.validate_mode("invalid")
        assert is_valid is False

    def test_default_mode_forbids_claude(self):
        """Test that default mode forbids Claude execution."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            config = manager.get_mode_config()
            assert config.get('allow_claude') is False
        finally:
            manager.set_mode(original)

    def test_default_mode_forbids_mixed(self):
        """Test that default mode forbids mixed execution."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            config = manager.get_mode_config()
            assert config.get('allow_mixed') is False
        finally:
            manager.set_mode(original)

    def test_adaptive_mode_allows_claude(self):
        """Test that adaptive mode allows Claude."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            config = manager.get_mode_config()
            assert config.get('allow_claude') is True
        finally:
            manager.set_mode(original)

    def test_adaptive_mode_allows_mixed(self):
        """Test that adaptive mode allows mixed execution."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            config = manager.get_mode_config()
            assert config.get('allow_mixed') is True
        finally:
            manager.set_mode(original)

    def test_claude_min_forbids_ollama(self):
        """Test that claude-min mode forbids Ollama."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            config = manager.get_mode_config()
            assert config.get('allow_ollama') is False
        finally:
            manager.set_mode(original)

    def test_claude_min_restricts_to_haiku(self):
        """Test that claude-min only allows Haiku model."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            models = manager.get_allowed_models()
            assert "claude-haiku-4-5" in models
            assert "claude-sonnet-4-6" not in models
        finally:
            manager.set_mode(original)

    def test_get_token_budget(self):
        """Test getting token budget for a mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            budget = manager.get_token_budget()
            assert budget is not None
            assert budget == 100000
        finally:
            manager.set_mode(original)

    def test_is_mode_allowed_operation(self):
        """Test checking if operation is allowed in mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            assert manager.is_mode_allowed("ollama_execution") is True
            assert manager.is_mode_allowed("claude_execution") is False
        finally:
            manager.set_mode(original)

    def test_state_file_persistence(self):
        """Test that mode state is persisted to file."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            # Create new manager instance
            manager2 = ModeManager()
            # Should load the same active mode
            assert manager2.get_active_mode() == "adaptive"
        finally:
            manager.set_mode(original)


class TestModeGuard:
    """Tests for ModeGuard."""

    def test_mode_guard_initialization(self):
        """Test mode guard initializes."""
        guard = ModeGuard()
        assert guard.mode_manager is not None

    def test_check_operation_allowed_valid(self):
        """Test checking allowed operation doesn't raise."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)
            # Should not raise
            guard.check_operation_allowed("ollama_execution")
        finally:
            manager.set_mode(original)

    def test_check_operation_allowed_invalid(self):
        """Test checking forbidden operation raises."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)
            # Should raise
            with pytest.raises(ModeViolationError):
                guard.check_claude_execution_allowed()
        finally:
            manager.set_mode(original)

    def test_check_claude_execution_allowed_in_adaptive(self):
        """Test Claude execution allowed in adaptive mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            guard = ModeGuard(manager)
            # Should not raise
            guard.check_claude_execution_allowed()
        finally:
            manager.set_mode(original)

    def test_check_claude_execution_forbidden_in_default(self):
        """Test Claude execution forbidden in default mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)
            # Should raise
            with pytest.raises(ModeViolationError) as exc_info:
                guard.check_claude_execution_allowed()
            assert "forbidden" in str(exc_info.value).lower()
            assert "default" in str(exc_info.value).lower()
        finally:
            manager.set_mode(original)

    def test_check_mixed_execution_forbidden_in_default(self):
        """Test mixed execution forbidden in default mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)
            with pytest.raises(ModeViolationError):
                guard.check_mixed_execution_allowed()
        finally:
            manager.set_mode(original)

    def test_check_mixed_execution_allowed_in_adaptive(self):
        """Test mixed execution allowed in adaptive mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            guard = ModeGuard(manager)
            # Should not raise
            guard.check_mixed_execution_allowed()
        finally:
            manager.set_mode(original)

    def test_check_model_allowed_in_mode(self):
        """Test model allowlist enforcement."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            guard = ModeGuard(manager)
            # Should not raise
            guard.check_model_allowed("claude-haiku-4-5")
        finally:
            manager.set_mode(original)

    def test_check_model_forbidden_in_mode(self):
        """Test forbidden model raises."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            guard = ModeGuard(manager)
            with pytest.raises(ModeViolationError):
                guard.check_model_allowed("claude-opus-4-6")
        finally:
            manager.set_mode(original)

    def test_check_token_budget_within_limit(self):
        """Test token budget check within limit doesn't raise."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            guard = ModeGuard(manager)
            # Should not raise (within budget)
            guard.check_token_budget(50000)
        finally:
            manager.set_mode(original)

    def test_check_token_budget_exceeds_limit(self):
        """Test token budget check exceeding limit raises."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            guard = ModeGuard(manager)
            with pytest.raises(ModeViolationError):
                guard.check_token_budget(150000)
        finally:
            manager.set_mode(original)

    def test_get_mode_status(self):
        """Test getting mode status."""
        manager = ModeManager()
        guard = ModeGuard(manager)
        status = guard.get_mode_status()
        assert "active_mode" in status
        assert "constraints" in status
        assert "status" in status
        assert status["status"] == "ACTIVE"

    def test_mode_is_binding(self):
        """Test that mode constraints are binding (cannot be bypassed)."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)

            # Attempting to use Claude in default mode should fail
            with pytest.raises(ModeViolationError) as exc_info:
                guard.check_claude_execution_allowed()

            # Error message should clearly state it's binding
            assert "binding" in str(exc_info.value).lower() or \
                   "forbidden" in str(exc_info.value).lower() or \
                   "hard" in str(exc_info.value).lower()
        finally:
            manager.set_mode(original)


class TestModeSystemIntegration:
    """Integration tests for the mode system."""

    def test_default_mode_workflow(self):
        """Test workflow in default (Ollama-only) mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)

            # Ollama operations should be allowed
            guard.check_ollama_execution_allowed()

            # Claude operations should fail
            with pytest.raises(ModeViolationError):
                guard.check_claude_execution_allowed()

            # Mixed operations should fail
            with pytest.raises(ModeViolationError):
                guard.check_mixed_execution_allowed()
        finally:
            manager.set_mode(original)

    def test_adaptive_mode_workflow(self):
        """Test workflow in adaptive mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            guard = ModeGuard(manager)

            # All operations should be allowed
            guard.check_ollama_execution_allowed()
            guard.check_claude_execution_allowed()
            guard.check_mixed_execution_allowed()
        finally:
            manager.set_mode(original)

    def test_claude_min_mode_workflow(self):
        """Test workflow in claude-min mode."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            guard = ModeGuard(manager)

            # Claude operations should be allowed
            guard.check_claude_execution_allowed()

            # Ollama operations should fail
            with pytest.raises(ModeViolationError):
                guard.check_ollama_execution_allowed()

            # Only Haiku model allowed
            guard.check_model_allowed("claude-haiku-4-5")
            with pytest.raises(ModeViolationError):
                guard.check_model_allowed("claude-sonnet-4-6")

            # Token budget enforced
            guard.check_token_budget(50000)
            with pytest.raises(ModeViolationError):
                guard.check_token_budget(150000)
        finally:
            manager.set_mode(original)

    def test_mode_changes_take_effect(self):
        """Test that mode changes take immediate effect."""
        manager = ModeManager()
        guard = ModeGuard(manager)
        original = manager.get_active_mode()

        try:
            # Start in default
            manager.set_mode("default")
            with pytest.raises(ModeViolationError):
                guard.check_claude_execution_allowed()

            # Switch to adaptive
            manager.set_mode("adaptive")
            guard.check_claude_execution_allowed()  # Should not raise

            # Switch back to default
            manager.set_mode("default")
            with pytest.raises(ModeViolationError):
                guard.check_claude_execution_allowed()
        finally:
            manager.set_mode(original)
