"""Canonical Ollama model and context policy. Single source of truth.

Static policy: .claude/config/ollama.yaml (state_file, default_model, profiles, runtime).
Runtime state: .claude/state/ollama_model_state.json (default_model only).

Resolution (config-driven order):
  model: per_invocation_override > profile.model > state.default_model > config.default_model
  prompt_budget: per_invocation_override > profile.prompt_budget_chars > global_prompt_budget_chars
  num_ctx: per_invocation_override > profile.num_ctx_tokens > global_num_ctx_tokens

Alias-safe: validate and set only against /api/tags; resolve alias to installed tag; no /api/show
or auto_pull. Missing models fail clearly.
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_MODEL_FALLBACK = "qwen2.5-14b:research"
DEFAULT_PROMPT_BUDGET_CHARS = 12_000
DEFAULT_NUM_CTX_TOKENS = 8192

OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
OLLAMA_TIMEOUT = 5


class OllamaUnavailableError(Exception):
    """Raised when Ollama is not reachable (service down or not installed)."""


class ModelNotFoundError(Exception):
    """Raised when the requested model is not in the list of available models."""


class OllamaModelManager:
    """
    Loads policy from .claude/config/ollama.yaml and mutable state from state_file.
    State file path comes from config (state_file); state holds default_model.
    No script-based switching; no duplicate source of truth.
    """

    CONFIG_FILE = Path(".claude") / "config" / "ollama.yaml"

    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root).resolve() if project_root else Path.cwd().resolve()
        self._config_path = self.project_root / self.CONFIG_FILE
        self._config_cache: dict[str, Any] | None = None

    def _load_full_config(self) -> dict[str, Any]:
        """Load full ollama.yaml. Cached for same manager instance."""
        if self._config_cache is not None:
            return self._config_cache
        if not self._config_path.exists():
            self._config_cache = {}
            return self._config_cache
        try:
            import yaml
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config_cache = yaml.safe_load(f) or {}
            return self._config_cache
        except Exception:
            self._config_cache = {}
            return self._config_cache

    def _state_path(self) -> Path:
        """State file path from config or default."""
        cfg = self._load_full_config()
        state_file = (cfg.get("state_file") or ".claude/state/ollama_model_state.json").strip()
        if state_file.startswith(".claude"):
            return self.project_root / state_file.lstrip("/")
        return self.project_root / state_file

    def _load_state(self) -> dict[str, Any]:
        """Load state dict. Uses default_model; backward compat active_model."""
        path = self._state_path()
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Normalize: prefer default_model, fall back to active_model
            if "default_model" not in data and "active_model" in data:
                data["default_model"] = data["active_model"]
            return data
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_state(self, default_model: str) -> None:
        """Persist default_model to state file. Does not touch config."""
        path = self._state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "default_model": default_model,
            "last_updated": datetime.now().isoformat(),
            "last_updated_by": "ollama_model_manager",
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def list_models(self) -> list[str]:
        """
        Discover available models from local Ollama (GET /api/tags only).
        No /api/show or auto_pull. Raises OllamaUnavailableError if unreachable.
        """
        try:
            req = urllib.request.Request(OLLAMA_TAGS_URL)
            with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as e:
            raise OllamaUnavailableError(
                "Ollama is not available. Is it running? (e.g. start Ollama and ensure localhost:11434 is reachable)."
            ) from e
        except (json.JSONDecodeError, KeyError) as e:
            raise OllamaUnavailableError("Ollama returned invalid response.") from e

    def _resolve_alias_to_installed(self, model: str) -> str | None:
        """
        Resolve alias to an installed tag. Exact match or first tag that starts with model name.
        Uses tags only; no /api/show. Returns None if no match.
        """
        available = self.list_models()
        if model in available:
            return model
        # Prefix match: e.g. "qwen2.5-14b:research" matches "qwen2.5-14b:research" or "qwen2.5-14b:research-q4_0"
        for tag in available:
            if tag == model or tag.startswith(model + ":") or (":" in model and tag.startswith(model.split(":")[0] + ":")):
                return tag
        for tag in available:
            if model in tag:
                return tag
        return None

    def get_global_default(self) -> str:
        """
        Global default model: state.default_model > config.default_model > fallback.
        Does not consider profiles; does not mutate state.
        """
        state = self._load_state()
        if state.get("default_model"):
            return state["default_model"]
        cfg = self._load_full_config()
        if cfg.get("default_model"):
            return cfg["default_model"]
        try:
            available = self.list_models()
            if available:
                return available[0]
        except OllamaUnavailableError:
            pass
        return DEFAULT_MODEL_FALLBACK

    def get_profile_config(self, profile_name: str | None) -> dict[str, Any]:
        """Return profile config (model, prompt_budget_chars, num_ctx_tokens, params, ...). Empty if missing."""
        if not profile_name:
            return {}
        profiles = self._load_full_config().get("profiles") or {}
        return dict(profiles.get(profile_name) or {})

    def get_profiles(self) -> dict[str, dict[str, Any]]:
        """Return all profile configs. Read-only."""
        return dict(self._load_full_config().get("profiles") or {})

    def _unknown_profile_fallback_to_default(self) -> bool:
        """From config: when profile unknown, use global default."""
        return self._load_full_config().get("unknown_profile_fallback_to_default", True)

    def resolve_model(
        self,
        override: str | None = None,
        profile: str | None = None,
    ) -> tuple[str, str]:
        """
        Resolve model: per_invocation_override > profile.model > state.default_model > config.default_model.
        Returns (model_str, source). Does not mutate state.
        """
        if override and override.strip():
            return override.strip(), "per_invocation_override"
        if profile:
            prof = self.get_profile_config(profile)
            if prof.get("model"):
                return prof["model"], "profile_model"
        return self.get_global_default(), "state_default_model" if self._load_state().get("default_model") else "config_default_model"

    def get_prompt_budget(
        self,
        profile: str | None = None,
        override_chars: int | None = None,
    ) -> int:
        """
        Prompt+context budget (chars): override > profile.prompt_budget_chars > global_prompt_budget_chars.
        Respects strict_prompt_budget_enforcement from config.
        """
        if override_chars is not None and override_chars >= 0:
            return override_chars
        cfg = self._load_full_config()
        if profile:
            prof = (cfg.get("profiles") or {}).get(profile) or {}
            if prof.get("prompt_budget_chars") is not None:
                return int(prof["prompt_budget_chars"])
        global_budget = cfg.get("global_prompt_budget_chars")
        if global_budget is not None:
            return int(global_budget)
        return DEFAULT_PROMPT_BUDGET_CHARS

    def get_num_ctx(
        self,
        profile: str | None = None,
        override_tokens: int | None = None,
    ) -> int:
        """
        Context window (tokens): override > profile.num_ctx_tokens > global_num_ctx_tokens.
        Conservative defaults for CPU-heavy setups.
        """
        if override_tokens is not None and override_tokens >= 0:
            return override_tokens
        cfg = self._load_full_config()
        if profile:
            prof = (cfg.get("profiles") or {}).get(profile) or {}
            if prof.get("num_ctx_tokens") is not None:
                return int(prof["num_ctx_tokens"])
        global_ctx = cfg.get("global_num_ctx_tokens")
        if global_ctx is not None:
            return int(global_ctx)
        return DEFAULT_NUM_CTX_TOKENS

    def get_active_model(self) -> str:
        """Alias for get_global_default() for backward compatibility."""
        return self.get_global_default()

    def set_active_model(self, model: str) -> str:
        """
        Set global default model. Validates via tags only (alias-safe); resolves alias to installed tag.
        strict_model_validation and require_alias_resolution from config. No auto_pull.
        """
        cfg = self._load_full_config()
        runtime = cfg.get("runtime") or {}
        strict = cfg.get("strict_model_validation", True)
        require_alias = runtime.get("require_alias_resolution", True)

        available = self.list_models()
        if require_alias or strict:
            resolved = self._resolve_alias_to_installed(model)
            if resolved is None:
                raise ModelNotFoundError(
                    f"Model {model!r} is not available (validate_via_tags). Available: {', '.join(available[:15])}"
                    + (" ..." if len(available) > 15 else "")
                )
            model = resolved
        else:
            exact = next(
                (m for m in available if m == model or m.startswith(model + ":") or model in m),
                None,
            )
            if exact is None:
                raise ModelNotFoundError(
                    f"Model {model!r} is not available. Available: {', '.join(available[:15])}"
                    + (" ..." if len(available) > 15 else "")
                )
            model = exact

        self._save_state(model)
        return model

    def is_model_forbidden_for_default_mode(self, model_name: str) -> bool:
    forbidden = self._get_forbidden_models()
    return model_name in forbidden

    def validate_model(self, model: str) -> tuple[bool, str]:
        """
        Check if model is available via /api/tags only. Alias resolved to installed tag.
        No /api/show, no pull. Returns (True, message) or (False, error_message).
        """
        try:
            available = self.list_models()
        except OllamaUnavailableError as e:
            return False, str(e)
        resolved = self._resolve_alias_to_installed(model)
        if resolved is not None:
            return True, f"Model {model!r} resolves to installed tag {resolved!r}."
        return False, f"Model {model!r} not found. Available: {', '.join(available[:15])}" + (" ..." if len(available) > 15 else "")
