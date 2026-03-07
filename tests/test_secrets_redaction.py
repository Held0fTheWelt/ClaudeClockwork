"""Phase 34 — Secrets store and redaction in logs."""
from __future__ import annotations

import os

import pytest

from claudeclockwork.core.secrets.store import get_secret, safe_display, redact_for_log


def test_safe_display_redacts() -> None:
    raw = "api_key=sk-12345678901234567890"
    displayed = safe_display(raw)
    assert "sk-12345678901234567890" not in displayed
    assert "***REDACTED***" in displayed or "REDACTED" in displayed


def test_redact_for_log_structure() -> None:
    data = {"token": "secret123", "n": 1}
    out = redact_for_log(data)
    assert out.get("n") == 1
    assert out.get("token") == "***REDACTED***"
    assert "secret123" not in str(out)


def test_get_secret_from_env() -> None:
    os.environ["CLOCKWORK_TEST_KEY"] = "val"
    try:
        assert get_secret("test_key", env_prefix="CLOCKWORK_") == "val"
    finally:
        os.environ.pop("CLOCKWORK_TEST_KEY", None)
