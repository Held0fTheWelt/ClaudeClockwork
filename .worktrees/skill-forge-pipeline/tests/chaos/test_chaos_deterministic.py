"""Phase 39 — Chaos scenarios: timeout, CAS corruption, stubbed failure. Deterministic."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.cas.store import put, get
from claudeclockwork.workers.retry import is_retryable


def test_timeout_retryable() -> None:
    assert is_retryable({"status": "error", "error": "timeout"}) is True


def test_cas_corruption_detected() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        h = put(root, b"good")
        (root / "objects" / h[:2] / h).write_bytes(b"tampered")
        assert get(root, h) is None


def test_policy_denied_not_retryable() -> None:
    assert is_retryable({"status": "error", "errors": [{"code": "policy_denied"}]}) is False