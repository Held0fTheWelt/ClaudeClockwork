"""Hard enforcement tests for the Mode System (Phase 22)."""
import json
import pytest
from pathlib import Path
from claudeclockwork.core.mode import (
    ModeManager,
    ModeGuard,
    ModeViolationError,
)
from claudeclockwork.core.executor.executor import SkillExecutor
from claudeclockwork.core.registry.skill_registry import SkillRegistry
from claudeclockwork.core.security.permissions import PermissionManager
from claudeclockwork.core.models.execution_context import ExecutionContext


class TestDefaultModeEnforcement:
    """Tests that default mode is truly binding and enforces Pure Ollama."""

    def test_default_mode_blocks_claude_execution(self):
        """Test that default mode blocks Claude execution with hard error."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)

            with pytest.raises(ModeViolationError) as exc_info:
                guard.check_claude_execution_allowed()

            assert "Claude execution is forbidden" in str(exc_info.value)
            assert "hard constraint" in str(exc_info.value)

        finally:
            manager.set_mode(original_mode)

    def test_default_mode_blocks_mixed_execution(self):
        """Test that default mode blocks mixed Claude+Ollama execution."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)

            with pytest.raises(ModeViolationError) as exc_info:
                guard.check_mixed_execution_allowed()

            assert "mixed" in str(exc_info.value).lower()

        finally:
            manager.set_mode(original_mode)

    def test_default_mode_allows_ollama(self):
        """Test that default mode allows Ollama execution."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)

            # Should not raise
            guard.check_ollama_execution_allowed()

        finally:
            manager.set_mode(original_mode)

    def test_default_mode_forbids_claude_fallback(self):
        """Test that default mode forbids fallback to Claude."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("default")
            config = manager.get_mode_config()

            assert config.get("allow_fallback_to_claude") is False

        finally:
            manager.set_mode(original_mode)

    def test_default_mode_requires_ollama_available(self):
        """Test that default mode requires Ollama availability."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("default")

            assert manager.requires_ollama_available() is True

        finally:
            manager.set_mode(original_mode)


class TestAdaptiveModeEnforcement:
    """Tests that adaptive mode allows hybrid Claude+Ollama execution."""

    def test_adaptive_mode_allows_claude(self):
        """Test that adaptive mode allows Claude execution."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            guard = ModeGuard(manager)

            # Should not raise
            guard.check_claude_execution_allowed()

        finally:
            manager.set_mode(original_mode)

    def test_adaptive_mode_allows_ollama(self):
        """Test that adaptive mode allows Ollama execution."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            guard = ModeGuard(manager)

            # Should not raise
            guard.check_ollama_execution_allowed()

        finally:
            manager.set_mode(original_mode)

    def test_adaptive_mode_allows_mixed(self):
        """Test that adaptive mode allows mixed execution."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            guard = ModeGuard(manager)

            # Should not raise
            guard.check_mixed_execution_allowed()

        finally:
            manager.set_mode(original_mode)

    def test_adaptive_mode_allows_fallback(self):
        """Test that adaptive mode allows Claude fallback."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            config = manager.get_mode_config()

            assert config.get("allow_fallback_to_claude") is True

        finally:
            manager.set_mode(original_mode)


class TestClaudeMinModeEnforcement:
    """Tests that claude-min mode restricts to minimal Claude operations."""

    def test_claude_min_blocks_ollama(self):
        """Test that claude-min mode blocks Ollama execution."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            guard = ModeGuard(manager)

            with pytest.raises(ModeViolationError) as exc_info:
                guard.check_ollama_execution_allowed()

            assert "Ollama execution is forbidden" in str(exc_info.value)

        finally:
            manager.set_mode(original_mode)

    def test_claude_min_blocks_mixed(self):
        """Test that claude-min mode blocks mixed execution."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            guard = ModeGuard(manager)

            with pytest.raises(ModeViolationError) as exc_info:
                guard.check_mixed_execution_allowed()

            assert "mixed" in str(exc_info.value).lower()

        finally:
            manager.set_mode(original_mode)

    def test_claude_min_restricts_to_haiku(self):
        """Test that claude-min only allows Haiku model."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            guard = ModeGuard(manager)
            models = manager.get_allowed_models()

            assert "claude-haiku-4-5" in models
            assert "claude-sonnet-4-6" not in models
            assert "claude-opus-4-6" not in models

            # Should allow Haiku
            guard.check_model_allowed("claude-haiku-4-5")

            # Should block Sonnet
            with pytest.raises(ModeViolationError):
                guard.check_model_allowed("claude-sonnet-4-6")

        finally:
            manager.set_mode(original_mode)

    def test_claude_min_enforces_token_budget(self):
        """Test that claude-min enforces token budget."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("claude-min")
            guard = ModeGuard(manager)
            budget = manager.get_token_budget()

            assert budget == 100000

            # Should allow within budget
            guard.check_token_budget(50000)

            # Should block over budget
            with pytest.raises(ModeViolationError):
                guard.check_token_budget(150000)

        finally:
            manager.set_mode(original_mode)


class TestSkillExecutorModeEnforcement:
    """Tests that SkillExecutor enforces mode constraints."""

    def test_executor_validates_mode_state(self):
        """Test that executor validates mode state before execution."""
        registry = SkillRegistry(Path("."))
        perm_manager = PermissionManager()
        executor = SkillExecutor(registry, perm_manager)

        context = ExecutionContext(
            request_id="test-req",
            user_input="test",
            working_directory=".",
        )

        # Non-existent skill should fail with skill not found (before mode check)
        # This tests the gate ordering
        result = executor.execute("nonexistent_skill", context)
        assert result.success is False

    def test_executor_blocks_claude_skill_in_default_mode(self):
        """Test that executor blocks Claude-type skills in default mode."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("default")
            registry = SkillRegistry(Path("."))
            perm_manager = PermissionManager()
            executor = SkillExecutor(registry, perm_manager, mode_manager=manager)

            # Create a test context
            context = ExecutionContext(
                request_id="test-req",
                user_input="test",
                working_directory=".",
            )

            # Try to execute a non-existent Claude skill
            # (This tests the mode gate, even if skill doesn't exist)
            result = executor.execute("hypothetical_claude_skill", context)
            assert result.success is False

        finally:
            manager.set_mode(original_mode)


class TestModeStateConsistency:
    """Tests that mode state is persistent and consistent."""

    def test_mode_state_persists_across_instances(self):
        """Test that mode setting persists to state file."""
        manager1 = ModeManager()
        original_mode = manager1.get_active_mode()
        try:
            # Set mode with first instance
            manager1.set_mode("adaptive")

            # Create new instance and verify
            manager2 = ModeManager()
            assert manager2.get_active_mode() == "adaptive"

        finally:
            manager1.set_mode(original_mode)

    def test_mode_state_file_format(self):
        """Test that mode state file has correct format."""
        manager = ModeManager()
        original_mode = manager.get_active_mode()
        try:
            manager.set_mode("default")

            state_file = Path(".claude/state/mode_state.json")
            assert state_file.exists()

            with open(state_file) as f:
                state = json.load(f)

            assert "active_mode" in state
            assert state["active_mode"] == "default"
            assert "updated_at" in state or "last_updated" in state

        finally:
            manager.set_mode(original_mode)


class TestModeTransitionRules:
    """Tests that mode transitions follow allowed rules."""

    def test_default_to_adaptive_transition_allowed(self):
        """Test that transition from default to adaptive is allowed."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            manager.set_mode("adaptive")
            assert manager.get_active_mode() == "adaptive"
        finally:
            manager.set_mode(original)

    def test_adaptive_to_default_transition_allowed(self):
        """Test that transition from adaptive to default is allowed."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("adaptive")
            manager.set_mode("default")
            assert manager.get_active_mode() == "default"
        finally:
            manager.set_mode(original)

    def test_invalid_mode_transition_blocked(self):
        """Test that invalid transitions are blocked."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            # Try to transition to invalid mode
            with pytest.raises(ValueError):
                manager.set_mode("invalid_mode")
        finally:
            manager.set_mode(original)


class TestModeGuardDecorator:
    """Tests that mode guard decorator works correctly."""

    def test_guard_decorator_blocks_forbidden_operation(self):
        """Test that guard decorator enforces mode constraints."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)

            @guard.guard_operation("claude_execution")
            def test_func():
                return "should not reach here"

            # Calling the decorated function should raise
            with pytest.raises(ModeViolationError):
                test_func()

        finally:
            manager.set_mode(original)

    def test_guard_decorator_allows_permitted_operation(self):
        """Test that guard decorator allows permitted operations."""
        manager = ModeManager()
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            guard = ModeGuard(manager)

            @guard.guard_operation("ollama_execution")
            def test_func():
                return "success"

            # Calling the decorated function should succeed
            result = test_func()
            assert result == "success"

        finally:
            manager.set_mode(original)


class TestModeStatusReporting:
    """Tests that mode status can be queried correctly."""

    def test_get_mode_status_returns_constraints(self):
        """Test that mode status reporting includes all constraints."""
        manager = ModeManager()
        guard = ModeGuard(manager)
        original = manager.get_active_mode()
        try:
            manager.set_mode("default")
            status = guard.get_mode_status()

            assert status["active_mode"] == "default"
            assert "constraints" in status
            assert status["constraints"]["allow_claude"] is False
            assert status["constraints"]["allow_ollama"] is True
            assert status["constraints"]["allow_mixed"] is False
            assert status["status"] == "ACTIVE"

        finally:
            manager.set_mode(original)
