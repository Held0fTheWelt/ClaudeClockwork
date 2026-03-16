"""Phase 39 — Retry policy: deterministic for error codes."""
from __future__ import annotations

import pytest

from claudeclockwork.workers.retry import is_retryable
from claudeclockwork.core.errors import POLICY_DENIED, VALIDATION_FAILED


def test_retryable_timeout() -> None:
    assert is_retryable({"status": "error", "error": "timeout"}) is True


def test_non_retryable_policy_denied() -> None:
    assert is_retryable({"status": "error", "errors": [{"code": POLICY_DENIED}]}) is False


def test_non_retryable_validation_failed() -> None:
    assert is_retryable({"status": "error", "errors": [{"code": VALIDATION_FAILED}]}) is False