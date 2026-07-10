"""Local Ollama runtime: config loading and a minimal blocking client."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import httpx
import yaml

DEFAULT_FORBIDDEN = (
    "qwen2.5:32b",
    "qwen2.5-coder:32b",
    "qwen2.5:72b",
    "llama3.3:70b",
    "llama2:70b",
)


class ForbiddenModelError(RuntimeError):
    """Raised when a forbidden model is explicitly requested."""


@dataclass(frozen=True)
class RuntimeConfig:
    base_url: str = "http://127.0.0.1:11434"
    default_model: str = "qwen3:8b"
    fallback_model: str = "phi4"
    forbidden_models: tuple[str, ...] = DEFAULT_FORBIDDEN
    connect_timeout: float = 10.0
    health_timeout: float = 15.0
    request_timeout: float = 300.0
    num_ctx: int = 4096


def load_runtime_config(path: str | Path | None = None) -> RuntimeConfig:
    candidate = Path(path) if path else Path("clockwork.yaml")
    if not candidate.exists():
        return RuntimeConfig()
    raw = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
    section = raw.get("ollama") or {}
    timeouts = section.get("timeouts") or {}
    defaults = RuntimeConfig()
    return RuntimeConfig(
        base_url=section.get("base_url", defaults.base_url),
        default_model=section.get("default_model", defaults.default_model),
        fallback_model=section.get("fallback_model", defaults.fallback_model),
        forbidden_models=tuple(section.get("forbidden_models", defaults.forbidden_models)),
        connect_timeout=float(timeouts.get("connect", defaults.connect_timeout)),
        health_timeout=float(timeouts.get("health", defaults.health_timeout)),
        request_timeout=float(timeouts.get("request", defaults.request_timeout)),
        num_ctx=int(section.get("num_ctx", defaults.num_ctx)),
    )


class OllamaClient:
    def __init__(self, config: RuntimeConfig | None = None) -> None:
        self.config = config or load_runtime_config()

    def is_available(self) -> bool:
        try:
            response = httpx.get(
                f"{self.config.base_url}/api/tags",
                timeout=self.config.health_timeout,
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def _post_generate(self, model: str, prompt: str, system: str | None):
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_ctx": self.config.num_ctx},
        }
        if system:
            payload["system"] = system
        return httpx.post(
            f"{self.config.base_url}/api/generate",
            json=payload,
            timeout=self.config.request_timeout,
        )

    def generate(
        self, prompt: str, model: str | None = None, system: str | None = None
    ) -> str:
        chosen = model or self.config.default_model
        if chosen in self.config.forbidden_models:
            raise ForbiddenModelError(
                f"Model '{chosen}' is forbidden (GPU-first constraint, ADR-CW-0007)."
            )
        response = self._post_generate(chosen, prompt, system)
        if response.status_code == 404 and chosen != self.config.fallback_model:
            response = self._post_generate(self.config.fallback_model, prompt, system)
        response.raise_for_status()
        return str(response.json().get("response", ""))
