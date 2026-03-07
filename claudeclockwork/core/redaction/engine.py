"""Phase 23 — Redaction engine: apply rules to text/JSON, path normalization."""
from __future__ import annotations

import json
from typing import Any

from claudeclockwork.core.redaction.rules import REDACTION_PATTERNS


def redact_text(text: str) -> str:
    """Apply redaction patterns to text. Returns redacted string."""
    out = text
    for pattern, repl in REDACTION_PATTERNS:
        out = pattern.sub(repl, out)
    return out


def redact_json(data: Any) -> Any:
    """Redact string values in JSON-like structures. Returns new structure."""
    if isinstance(data, dict):
        return {k: redact_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [redact_json(v) for v in data]
    if isinstance(data, str):
        return redact_text(data)
    return data
