"""Phase 35 — Retry and idempotency tests."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.workers.retry import is_retryable, with_retry, idempotency_get, idempotency_set


def test_policy_denied_not_retryable() -> None:
    assert is_retryable({"status": "error", "errors": [{"code": "policy_denied"}]}) is False


def test_timeout_retryable() -> None:
    assert is_retryable({"status": "error", "error": "timeout"}) is True


def test_idempotency_set_get() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        idempotency_set(root, "k1", {"status": "ok", "x": 1})
        got = idempotency_get(root, "k1")
        assert got == {"status": "ok", "x": 1}
        assert idempotency_get(root, "k2") is None