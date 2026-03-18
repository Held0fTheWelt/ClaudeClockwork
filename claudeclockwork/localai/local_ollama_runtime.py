"""Local Ollama Runtime Configuration — Single Source of Truth.

Phase 22+: Hard-enforced local Ollama contract for Windows native backend.
All Ollama execution must read from this module to get canonical settings.

Do NOT hardcode Ollama URLs, timeouts, or model constraints elsewhere.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class LocalOllamaRuntimeConfig:
    """Loader and provider for canonical local Ollama runtime settings."""

    # SSOT config file location
    CONFIG_FILE = Path(".claude/config/local_ollama_runtime.yaml")

    # Cached config (loaded once per process)
    _config: dict[str, Any] | None = None

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load canonical local Ollama runtime config (cached)."""
        if cls._config is not None:
            return cls._config

        if not cls.CONFIG_FILE.exists():
            raise RuntimeError(
                f"Local Ollama runtime SSOT not found: {cls.CONFIG_FILE}\n"
                "This is required for all local Ollama execution.\n"
                "Run: .claude/tools/setup_local_ollama_runtime.py"
            )

        try:
            with open(cls.CONFIG_FILE) as f:
                cls._config = yaml.safe_load(f)
            return cls._config
        except Exception as e:
            raise RuntimeError(f"Failed to load local Ollama runtime config: {e}")

    @classmethod
    def get_connection(cls) -> dict[str, Any]:
        """Get canonical Ollama connection settings."""
        config = cls.load()
        return config.get("connection", {})

    @classmethod
    def get_base_url(cls) -> str:
        """Get canonical Ollama base URL (Windows native only)."""
        connection = cls.get_connection()
        return connection.get("base_url", "http://127.0.0.1:11434")

    @classmethod
    def get_default_model(cls) -> str:
        """Get default model for local execution."""
        config = cls.load()
        models = config.get("models", {})
        return models.get("default_model", "qwen3:8b")

    @classmethod
    def get_fallback_model(cls) -> str:
        """Get automatic fallback model (same tier as default)."""
        config = cls.load()
        models = config.get("models", {})
        return models.get("fallback_model", "phi4")

    @classmethod
    def get_default_num_ctx(cls) -> int:
        """Get default context window for GPU-first path."""
        config = cls.load()
        token_limits = config.get("token_limits", {})
        return token_limits.get("default_num_ctx", 4096)

    @classmethod
    def is_model_forbidden(cls, model_name: str) -> bool:
        """Check if model is in forbidden escalations list."""
        config = cls.load()
        models = config.get("models", {})
        forbidden = models.get("forbidden_escalations", [])
        return model_name in forbidden or any(
            model_name.startswith(f) for f in forbidden
        )

    @classmethod
    def get_forbidden_escalation_error(cls) -> str:
        """Get error message for forbidden model escalations."""
        config = cls.load()
        models = config.get("models", {})
        return models.get(
            "forbidden_escalation_error_message",
            "Automatic escalation to 32B/70B/72B models is forbidden in default mode.",
        )

    @classmethod
    def is_gpu_first_required(cls) -> bool:
        """Check if GPU-first execution is mandatory."""
        config = cls.load()
        runtime = config.get("runtime", {})
        return runtime.get("gpu_first_required", True)

    @classmethod
    def get_gpu_first_error(cls) -> str:
        """Get error message for GPU-first violations."""
        config = cls.load()
        runtime = config.get("runtime", {})
        return runtime.get(
            "gpu_first_error_message",
            "Local Ollama must use GPU. CPU-only execution not permitted.",
        )

    @classmethod
    def get_timeout(cls, operation_type: str) -> int:
        """Get timeout in seconds for a specific operation type."""
        config = cls.load()
        timeouts = config.get("timeouts", {})
        timeout_key = f"{operation_type}_timeout_seconds"

        defaults = {
            "connect": 10,
            "health": 15,
            "request": 300,
            "heavy": 600,
            "warmup": 120,
            "agent_step": 420,
        }

        return timeouts.get(timeout_key, defaults.get(operation_type, 300))

    @classmethod
    def get_all_timeouts(cls) -> dict[str, int]:
        """Get all timeout settings."""
        config = cls.load()
        return config.get("timeouts", {})

    @classmethod
    def is_mandatory_for_default_mode(cls) -> bool:
        """Check if Ollama is mandatory in default mode."""
        config = cls.load()
        connection = config.get("connection", {})
        return connection.get("is_mandatory_for_default_mode", True)

    @classmethod
    def get_max_loaded_models(cls) -> int:
        """Get maximum concurrent models (single-model constraint)."""
        config = cls.load()
        runtime = config.get("runtime", {})
        return runtime.get("max_loaded_models", 1)

    @classmethod
    def get_num_parallel(cls) -> int:
        """Get number of parallel inferences (single-request constraint)."""
        config = cls.load()
        runtime = config.get("runtime", {})
        return runtime.get("num_parallel", 1)

    @classmethod
    def is_cpu_only_degraded(cls) -> bool:
        """Check if CPU-only execution is marked as degraded."""
        config = cls.load()
        models = config.get("models", {})
        return models.get("cpu_only_models_degraded", True)

    @classmethod
    def get_governance_enforcement_level(cls) -> str:
        """Get enforcement level from governance settings."""
        config = cls.load()
        governance = config.get("governance", {})
        return governance.get("enforcement_level", "HARD")

    @classmethod
    def validate_config(cls) -> tuple[bool, str]:
        """Validate config integrity."""
        try:
            config = cls.load()

            # Check required top-level keys
            required_keys = [
                "version",
                "connection",
                "models",
                "token_limits",
                "runtime",
                "timeouts",
                "governance",
            ]
            for key in required_keys:
                if key not in config:
                    return False, f"Missing required section: {key}"

            # Validate connection
            connection = config["connection"]
            if "base_url" not in connection:
                return False, "Missing connection.base_url"

            # Validate models
            models = config["models"]
            if "default_model" not in models:
                return False, "Missing models.default_model"
            if "forbidden_escalations" not in models:
                return False, "Missing models.forbidden_escalations"

            # Validate runtime
            runtime = config["runtime"]
            if "max_loaded_models" not in runtime:
                return False, "Missing runtime.max_loaded_models"

            # Validate timeouts
            timeouts = config["timeouts"]
            required_timeouts = [
                "connect_timeout_seconds",
                "health_timeout_seconds",
                "request_timeout_seconds",
                "heavy_request_timeout_seconds",
                "warmup_timeout_seconds",
                "agent_step_timeout_seconds",
            ]
            for timeout_key in required_timeouts:
                if timeout_key not in timeouts:
                    return False, f"Missing timeouts.{timeout_key}"

            return True, "Config valid"

        except Exception as e:
            return False, f"Config validation error: {e}"

    @classmethod
    def to_dict(cls) -> dict[str, Any]:
        """Get entire config as dict (for debugging/audit)."""
        return cls.load()

    @classmethod
    def dump_yaml(cls) -> str:
        """Get config as YAML string (for logging)."""
        config = cls.load()
        return yaml.dump(config, default_flow_style=False)

    @staticmethod
    def is_model_forbidden_for_default_mode(model_name: str) -> bool:
        """Check if model is forbidden in default mode (GPU-first constraint).
        Returns True if forbidden, False if allowed."""
        forbidden_list = ['qwen2.5:32b', 'qwen2.5-coder:32b', 'qwen2.5:70b', 'qwen2.5-72b', 'llama3.3:70b', 'llama2:70b']
        return model_name in forbidden_list


def get_canonical_ollama_base_url() -> str:
    """Convenience function: get canonical Ollama URL."""
    return LocalOllamaRuntimeConfig.get_base_url()


def validate_model_not_forbidden(model_name: str) -> None:
    """Convenience function: validate model against forbidden list.

    Raises:
        RuntimeError: If model is in forbidden escalations.
    """
    if LocalOllamaRuntimeConfig.is_model_forbidden(model_name):
        raise RuntimeError(
            f"Model '{model_name}' is in forbidden escalations. "
            + LocalOllamaRuntimeConfig.get_forbidden_escalation_error()
        )
def get_operation_timeout(operation_type: str) -> int:
    """Convenience function: get timeout for operation type."""
    return LocalOllamaRuntimeConfig.get_timeout(operation_type)
