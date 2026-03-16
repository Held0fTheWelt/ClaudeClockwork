"""Phase 48 — Tests for scheduler: ordering, fairness, backpressure."""
from __future__ import annotations

import pytest

from claudeclockwork.scheduler.queue import JobQueue, PRIORITY_HIGH, PRIORITY_NORMAL, PRIORITY_LOW, QueueTelemetry


def test_ordering_respects_priority() -> None:
    q = JobQueue()
    q.enqueue({"id": "low"}, PRIORITY_LOW)
    q.enqueue({"id": "high"}, PRIORITY_HIGH)
    q.enqueue({"id": "normal"}, PRIORITY_NORMAL)
    assert q.dequeue()["id"] == "high"
    assert q.dequeue()["id"] == "normal"
    assert q.dequeue()["id"] == "low"
    assert q.dequeue() is None


def test_fairness_fifo_within_priority() -> None:
    q = JobQueue()
    q.enqueue({"id": "a"}, PRIORITY_NORMAL)
    q.enqueue({"id": "b"}, PRIORITY_NORMAL)
    assert q.dequeue()["id"] == "a"
    assert q.dequeue()["id"] == "b"


def test_backpressure_rejects_when_full() -> None:
    q = JobQueue(max_size=2)
    ok1, _ = q.enqueue({"id": "1"})
    ok2, _ = q.enqueue({"id": "2"})
    ok3, reason = q.enqueue({"id": "3"})
    assert ok1 and ok2
    assert not ok3 and reason == "backpressure"
    assert q.telemetry.backpressure_rejected == 1


def test_telemetry_counts() -> None:
    q = JobQueue()
    q.enqueue({"id": "1"})
    q.enqueue({"id": "2"})
    q.dequeue()
    t = q.telemetry.to_dict()
    assert t["enqueued"] == 2
    assert t["dequeued"] == 1
