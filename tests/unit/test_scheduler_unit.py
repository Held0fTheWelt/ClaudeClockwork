"""Unit test: scheduler (no I/O)."""
import pytest
from claudeclockwork.scheduler.queue import JobQueue, PRIORITY_HIGH


@pytest.mark.unit
def test_queue_unit() -> None:
    q = JobQueue()
    q.enqueue({"id": "1"}, PRIORITY_HIGH)
    assert q.dequeue()["id"] == "1"
