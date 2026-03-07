"""Phase 41 — Worker placement."""
from __future__ import annotations

import pytest

from claudeclockwork.optimizer.worker_placement import choose_worker


def test_choose_least_loaded() -> None:
    w = choose_worker(worker_loads={"w1": 2.0, "w2": 0.5})
    assert w == "w2"