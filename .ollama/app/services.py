"""Task Executor Service - Pure Python adapter for claudeclockwork.TaskExecutor.

Standalone service with no Flask dependency.
Wraps TaskExecutor, handles ImportError gracefully, provides serializable results.
"""
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TaskExecutorService:
    """Thin adapter over claudeclockwork.TaskExecutor.

    Handles:
    - Lazy import of claudeclockwork (may not be installed)
    - Singleton instance creation
    - Env var configuration
    - Error recovery for unavailable Ollama/Claude
    - Serializable result format
    """

    _instance: Optional["TaskExecutorService"] = None
    _executor = None
    _init_error: Optional[str] = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize TaskExecutor from claudeclockwork if available."""
        try:
            from claudeclockwork.core.executor.task_executor import TaskExecutor

            ollama_host = os.getenv("OLLAMA_HOST", "localhost")
            ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
            fallback_to_claude = os.getenv("OLLAMA_FALLBACK_TO_CLAUDE", "true").lower() == "true"

            TaskExecutorService._executor = TaskExecutor(
                ollama_host=ollama_host,
                ollama_port=ollama_port,
                fallback_to_claude=fallback_to_claude,
            )
            logger.info(
                "TaskExecutor initialized: ollama_host=%s, ollama_port=%d, fallback_to_claude=%s",
                ollama_host,
                ollama_port,
                fallback_to_claude,
            )
        except ImportError as e:
            TaskExecutorService._init_error = (
                f"claudeclockwork not installed: {e}. "
                "Install with: pip install -e .clockwork_integration/"
            )
            logger.warning(TaskExecutorService._init_error)
        except Exception as e:
            TaskExecutorService._init_error = f"TaskExecutor init failed: {e}"
            logger.error(TaskExecutorService._init_error, exc_info=True)

    def is_available(self) -> bool:
        """Check if TaskExecutor is available."""
        return TaskExecutorService._executor is not None

    def health_check(self) -> Dict[str, Any]:
        """Check Ollama and budget health.

        Returns:
            {
                "available": bool,
                "ollama_available": bool | None,
                "budget_status": str,
                "error": str | None,
            }
        """
        if not self.is_available():
            return {
                "available": False,
                "error": TaskExecutorService._init_error,
            }

        try:
            executor = TaskExecutorService._executor

            # Check Ollama availability
            ollama_available = False
            try:
                from claudeclockwork.localai.ollama_client import OllamaClient

                client = OllamaClient(
                    host=os.getenv("OLLAMA_HOST", "localhost"),
                    port=int(os.getenv("OLLAMA_PORT", "11434")),
                )
                ollama_available = client.is_available()
            except Exception as e:
                logger.debug("Ollama health check failed: %s", e)

            # Get budget status
            budget_status = "ok"
            if executor.token_budget:
                try:
                    remaining = executor.token_budget.remaining()
                    if remaining < 0:
                        budget_status = "exceeded"
                    elif remaining < executor.token_budget.limit * 0.2:
                        budget_status = "low"
                except Exception as e:
                    logger.debug("Token budget check failed: %s", e)

            return {
                "available": True,
                "ollama_available": ollama_available,
                "budget_status": budget_status,
                "total_cost": executor.cost_tracker.total_cost() if executor.cost_tracker else 0.0,
                "total_tokens": executor.token_budget.used if executor.token_budget else 0,
            }
        except Exception as e:
            logger.error("Health check failed: %s", e, exc_info=True)
            return {
                "available": False,
                "error": str(e),
            }

    def execute_task(
        self,
        task_id: str,
        escalation_level: int,
        inputs: Dict[str, Any],
        preferred_models: Optional[list] = None,
        force_ollama: bool = False,
    ) -> Dict[str, Any]:
        """Execute task with intelligent routing.

        Args:
            task_id: Task identifier (for logging)
            escalation_level: 0-5 (L0-L5)
            inputs: Dict with 'prompt' key (required), 'system_prompt' optional
            preferred_models: Preferred model names to try first
            force_ollama: If True, fail rather than fall back to Claude

        Returns:
            {
                "success": bool,
                "target_worker": "ollama" | "claude_api" | "stop_ask_user",
                "model": str,
                "output": str,
                "cost": float,
                "cost_formatted": str,
                "tokens_used": int,
                "latency_ms": float,
                "error": str | None,
            }
        """
        if not self.is_available():
            return {
                "success": False,
                "error": TaskExecutorService._init_error,
            }

        try:
            # Validate inputs
            if "prompt" not in inputs:
                return {
                    "success": False,
                    "error": "Missing required key 'prompt' in inputs",
                }

            # Convert EscalationLevel to int if needed
            level_int = escalation_level.value if hasattr(escalation_level, 'value') else escalation_level

            if not (0 <= level_int <= 5):
                return {
                    "success": False,
                    "error": f"Invalid escalation_level {escalation_level}, must be 0-5",
                }

            executor = TaskExecutorService._executor

            # Execute task
            result = executor.execute_task(
                task_id=task_id,
                escalation_level=escalation_level,
                inputs=inputs,
                preferred_models=preferred_models,
                force_ollama=force_ollama,
            )

            # Normalize SkillResult to dict
            metadata = result.metadata or {}
            data = result.data or {}
            return {
                "success": result.success,
                "target_worker": metadata.get("target_worker", "unknown"),
                "model": metadata.get("model", "unknown"),
                "output": data.get("output", ""),
                "cost": metadata.get("cost", 0.0),
                "cost_formatted": metadata.get("cost_formatted", "$0.00"),
                "tokens_used": metadata.get("tokens_used", 0),
                "latency_ms": metadata.get("latency_ms", 0.0),
                "error": result.error,
            }

        except ImportError:
            return {
                "success": False,
                "error": "claudeclockwork not installed",
            }
        except Exception as e:
            logger.error("Task execution failed: %s", e, exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get cumulative cost and token usage stats."""
        if not self.is_available():
            return {"error": "TaskExecutor not available"}

        try:
            executor = TaskExecutorService._executor
            return {
                "total_cost": executor.cost_tracker.total_cost() if executor.cost_tracker else 0.0,
                "total_tokens": executor.token_budget.used if executor.token_budget else 0,
                "token_limit": executor.token_budget.limit if executor.token_budget else 0,
            }
        except Exception as e:
            logger.error("Failed to get stats: %s", e, exc_info=True)
            return {"error": str(e)}
