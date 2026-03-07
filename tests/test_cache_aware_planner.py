"""Phase 41 — Cache-aware planner."""
from __future__ import annotations

import pytest

from claudeclockwork.optimizer.cache_aware import plan_order


def test_plan_prefers_cas_ready() -> None:
    nodes = [{"id": "a", "input_artifact_refs": ["h1"]}, {"id": "b", "input_artifact_refs": ["h2"]}]
    order = plan_order(nodes, {"h1", "h2"})
    assert set(order) == {"a", "b"}
    assert order == sorted(order)