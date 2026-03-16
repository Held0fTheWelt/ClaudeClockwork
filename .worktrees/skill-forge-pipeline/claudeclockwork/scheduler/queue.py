"""Phase 48 — Job queue with priorities, fairness, backpressure, and telemetry."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

PRIORITY_HIGH = 0
PRIORITY_NORMAL = 1
PRIORITY_LOW = 2


@dataclass
class QueueTelemetry:
    """Queue telemetry: enqueue/dequeue counts and backpressure events."""
    enqueued: int = 0
    dequeued: int = 0
    backpressure_rejected: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "enqueued": self.enqueued,
            "dequeued": self.dequeued,
            "backpressure_rejected": self.backpressure_rejected,
        }


class JobQueue:
    """
    In-memory job queue with priorities (lower number = higher priority),
    fairness (FIFO within priority), and backpressure (max size).
    """

    def __init__(self, max_size: int = 0) -> None:
        self._max_size = max_size  # 0 = unbounded
        self._queues: dict[int, deque] = {
            PRIORITY_HIGH: deque(),
            PRIORITY_NORMAL: deque(),
            PRIORITY_LOW: deque(),
        }
        self._telemetry = QueueTelemetry()

    def enqueue(self, job: dict[str, Any], priority: int = PRIORITY_NORMAL) -> tuple[bool, str]:
        """
        Enqueue job. Returns (accepted, reason). On backpressure, rejects and increments telemetry.
        """
        if self._max_size > 0 and self.size() >= self._max_size:
            self._telemetry.backpressure_rejected += 1
            return False, "backpressure"
        p = priority if priority in self._queues else PRIORITY_NORMAL
        self._queues[p].append(job)
        self._telemetry.enqueued += 1
        return True, ""

    def dequeue(self) -> dict[str, Any] | None:
        """Dequeue next job (highest priority, FIFO within priority)."""
        for p in (PRIORITY_HIGH, PRIORITY_NORMAL, PRIORITY_LOW):
            if self._queues[p]:
                job = self._queues[p].popleft()
                self._telemetry.dequeued += 1
                return job
        return None

    def size(self) -> int:
        return sum(len(q) for q in self._queues.values())

    @property
    def telemetry(self) -> QueueTelemetry:
        return self._telemetry
