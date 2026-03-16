"""Phase 35 — Local worker and envelope tests."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.workers.local_worker import process_envelope
from claudeclockwork.workers.dispatcher import dispatch


def test_envelope_validation_required_fields() -> None:
    """Envelope must have job_id, idempotency_key, node_spec."""
    valid = {"job_id": "j0", "idempotency_key": "k0", "node_spec": {"id": "n0"}}
    for key in ("job_id", "idempotency_key", "node_spec"):
        assert key in valid

def test_envelope_processed() -> None:
    with tempfile.TemporaryDirectory() as d:
        envelope = {"job_id": "j1", "idempotency_key": "k1", "node_spec": {"id": "n1"}}
        out = process_envelope(envelope, d)
        assert out.get("status") == "ok"
        assert out.get("job_id") == "j1"


def test_dispatcher_idempotency() -> None:
    with tempfile.TemporaryDirectory() as d:
        envelope = {"job_id": "j2", "idempotency_key": "key2", "node_spec": {"id": "n2"}}
        r1 = dispatch(envelope, d)
        r2 = dispatch(envelope, d)
        assert r1.get("status") == "ok"
        assert r2.get("status") == "ok"
        assert r1.get("job_id") == r2.get("job_id")
        assert r1.get("result") == r2.get("result")
        # Second call returns cached
        assert (Path(d) / ".clockwork_runtime" / "idempotency" / "key2.json").exists()