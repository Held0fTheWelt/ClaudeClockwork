"""Phase 34 — Centralized secrets: load from env/config, never log raw, redact by default."""
from __future__ import annotations

import os
from typing import Any

from claudeclockwork.core.redaction.engine import redact_text


def get_secret(key: str, env_prefix: str = "CLOCKWORK_") -> str:
    """Load secret from env (e.g. CLOCKWORK_API_KEY). Never print; use safe_display for logs."""
    env_key = f"{env_prefix}{key.upper()}"
    return os.environ.get(env_key, "")


def safe_display(value: str) -> str:
    """Return redacted string for logging/telemetry. Never returns raw secret."""
    if not value:
        return ""
    return redact_text(value)


SECRET_KEYS = frozenset({"token", "secret", "api_key", "password", "auth"})

def redact_for_log(data: Any) -> Any:
    """Redact any structure for logging. Use in telemetry and runtime logs."""
    if isinstance(data, dict):
        return {k: ("***REDACTED***" if isinstance(v, str) and k.lower() in SECRET_KEYS else redact_for_log(v)) for k, v in data.items()}
    if isinstance(data, list):
        return [redact_for_log(v) for v in data]
    if isinstance(data, str):
        return redact_text(data)
    return data
