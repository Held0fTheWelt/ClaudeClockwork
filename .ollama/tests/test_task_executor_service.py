"""Tests for TaskExecutorService - fallback behavior and cost tracking.

Pure Python unit tests (no Flask dependency).
Uses unittest.mock to simulate Ollama unavailability and Claude API responses.
"""
import unittest
from unittest.mock import MagicMock, patch, call
from typing import Dict, Any

# Import the service
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.services import TaskExecutorService


class TestTaskExecutorServiceAvailability(unittest.TestCase):
    """Tests for TaskExecutorService initialization and availability."""

    def setUp(self):
        """Reset singleton before each test."""
        TaskExecutorService._instance = None
        TaskExecutorService._executor = None
        TaskExecutorService._init_error = None

    def test_not_available_when_claudeclockwork_not_installed(self):
        """When claudeclockwork is not installed, service returns graceful error."""
        with patch("app.services.logger"):
            # Simulate ImportError
            with patch("app.services.TaskExecutor", side_effect=ImportError("No module")):
                service = TaskExecutorService()
                self.assertFalse(service.is_available())
                self.assertIn("not installed", service._init_error)

    def test_health_check_unavailable(self):
        """Health check returns error when service unavailable."""
        with patch("app.services.logger"):
            with patch("app.services.TaskExecutor", side_effect=ImportError("No module")):
                service = TaskExecutorService()
                result = service.health_check()
                self.assertFalse(result["available"])
                self.assertIn("error", result)

    def test_execute_task_unavailable(self):
        """Execute task returns error when service unavailable."""
        with patch("app.services.logger"):
            with patch("app.services.TaskExecutor", side_effect=ImportError("No module")):
                service = TaskExecutorService()
                result = service.execute_task(
                    task_id="test",
                    escalation_level=1,
                    inputs={"prompt": "test"},
                )
                self.assertFalse(result["success"])
                self.assertIn("error", result)


class TestTaskExecutorServiceValidation(unittest.TestCase):
    """Tests for input validation."""

    def setUp(self):
        """Reset singleton and mock TaskExecutor."""
        TaskExecutorService._instance = None
        TaskExecutorService._executor = None
        TaskExecutorService._init_error = None

    @patch("app.services.TaskExecutor")
    def test_missing_prompt_in_inputs(self, mock_executor_class):
        """Execute task returns error when 'prompt' is missing."""
        mock_executor_class.return_value = MagicMock()
        service = TaskExecutorService()

        result = service.execute_task(
            task_id="test",
            escalation_level=1,
            inputs={"no_prompt": "value"},  # Missing 'prompt'
        )

        self.assertFalse(result["success"])
        self.assertIn("Missing required key", result["error"])

    @patch("app.services.TaskExecutor")
    def test_invalid_escalation_level_negative(self, mock_executor_class):
        """Execute task returns error for invalid escalation level (< 0)."""
        mock_executor_class.return_value = MagicMock()
        service = TaskExecutorService()

        result = service.execute_task(
            task_id="test",
            escalation_level=-1,
            inputs={"prompt": "test"},
        )

        self.assertFalse(result["success"])
        self.assertIn("Invalid escalation_level", result["error"])

    @patch("app.services.TaskExecutor")
    def test_invalid_escalation_level_too_high(self, mock_executor_class):
        """Execute task returns error for invalid escalation level (> 5)."""
        mock_executor_class.return_value = MagicMock()
        service = TaskExecutorService()

        result = service.execute_task(
            task_id="test",
            escalation_level=6,
            inputs={"prompt": "test"},
        )

        self.assertFalse(result["success"])
        self.assertIn("Invalid escalation_level", result["error"])


class TestTaskExecutorServiceExecution(unittest.TestCase):
    """Tests for task execution and result formatting."""

    def setUp(self):
        """Reset singleton and mock TaskExecutor."""
        TaskExecutorService._instance = None
        TaskExecutorService._executor = None
        TaskExecutorService._init_error = None

    @patch("app.services.TaskExecutor")
    def test_successful_ollama_execution(self, mock_executor_class):
        """Successful Ollama execution returns normalized result."""
        # Mock executor
        mock_executor = MagicMock()

        # Mock SkillResult
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = "Test output"
        mock_result.error = None
        mock_result.meta = {
            "target_worker": "ollama",
            "model": "qwen2.5-coder:32b",
            "cost": 0.0,
            "cost_formatted": "$0.00",
            "tokens_used": 500,
            "latency_ms": 5000.0,
        }

        mock_executor.execute_task.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        service = TaskExecutorService()
        result = service.execute_task(
            task_id="test_task",
            escalation_level=1,
            inputs={"prompt": "Write code"},
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["target_worker"], "ollama")
        self.assertEqual(result["model"], "qwen2.5-coder:32b")
        self.assertEqual(result["cost"], 0.0)
        self.assertEqual(result["tokens_used"], 500)

    @patch("app.services.TaskExecutor")
    def test_fallback_to_claude_when_ollama_unavailable(self, mock_executor_class):
        """When Ollama unavailable, system falls back to Claude."""
        # Mock executor
        mock_executor = MagicMock()

        # Mock SkillResult simulating fallback
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = "Test output"
        mock_result.error = None
        mock_result.meta = {
            "target_worker": "claude_api",
            "model": "claude-sonnet-4-6",
            "cost": 0.05,
            "cost_formatted": "$0.05",
            "tokens_used": 500,
            "latency_ms": 2000.0,
        }

        mock_executor.execute_task.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        service = TaskExecutorService()
        result = service.execute_task(
            task_id="test_task",
            escalation_level=1,
            inputs={"prompt": "Write code"},
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["target_worker"], "claude_api")
        self.assertEqual(result["model"], "claude-sonnet-4-6")
        self.assertGreater(result["cost"], 0.0)

    @patch("app.services.TaskExecutor")
    def test_force_ollama_fails_when_unavailable(self, mock_executor_class):
        """When force_ollama=True and Ollama unavailable, execution fails."""
        # Mock executor
        mock_executor = MagicMock()

        # Mock SkillResult for failure
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.output = ""
        mock_result.error = "Ollama unavailable and force_ollama=True"
        mock_result.meta = {
            "target_worker": "ollama",
            "model": None,
            "cost": 0.0,
            "cost_formatted": "$0.00",
            "tokens_used": 0,
            "latency_ms": 0.0,
        }

        mock_executor.execute_task.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        service = TaskExecutorService()
        result = service.execute_task(
            task_id="test_task",
            escalation_level=1,
            inputs={"prompt": "Write code"},
            force_ollama=True,
        )

        self.assertFalse(result["success"])
        self.assertIn("unavailable", result["error"])

    @patch("app.services.TaskExecutor")
    def test_l5_escalation_stops_and_asks_user(self, mock_executor_class):
        """L5 (user escalation) returns stop signal."""
        # Mock executor
        mock_executor = MagicMock()

        # Mock SkillResult for L5
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.output = ""
        mock_result.error = "L5: User approval required"
        mock_result.meta = {
            "target_worker": "stop_ask_user",
            "model": None,
            "cost": 0.0,
            "cost_formatted": "$0.00",
            "tokens_used": 0,
            "latency_ms": 0.0,
        }

        mock_executor.execute_task.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        service = TaskExecutorService()
        result = service.execute_task(
            task_id="test_task",
            escalation_level=5,
            inputs={"prompt": "Redesign orchestrator"},
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["target_worker"], "stop_ask_user")


class TestTaskExecutorServiceStats(unittest.TestCase):
    """Tests for stats tracking."""

    def setUp(self):
        """Reset singleton and mock TaskExecutor."""
        TaskExecutorService._instance = None
        TaskExecutorService._executor = None
        TaskExecutorService._init_error = None

    @patch("app.services.TaskExecutor")
    def test_get_stats_returns_cost_and_tokens(self, mock_executor_class):
        """Get stats returns cumulative cost and token usage."""
        # Mock executor with cost tracking
        mock_executor = MagicMock()
        mock_executor.cost_tracker.total_cost.return_value = 0.35
        mock_executor.token_budget.used = 1500
        mock_executor.token_budget.limit = 10000

        mock_executor_class.return_value = mock_executor

        service = TaskExecutorService()
        stats = service.get_stats()

        self.assertEqual(stats["total_cost"], 0.35)
        self.assertEqual(stats["total_tokens"], 1500)
        self.assertEqual(stats["token_limit"], 10000)


if __name__ == "__main__":
    unittest.main()
