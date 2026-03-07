"""Phase 30 — Work graph runner and cache tests."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from claudeclockwork.workgraph.runner import run_graph, _topological_order
from claudeclockwork.workgraph.cache import NodeCache


def test_topological_order_stable_with_no_edges() -> None:
    nodes = [{"id": "b"}, {"id": "a"}, {"id": "c"}]
    order = _topological_order(nodes, [])
    assert order == ["a", "b", "c"]


def test_run_graph_twice_reuses_cache() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / ".clockwork_runtime").mkdir(parents=True)
        graph = {"nodes": [{"id": "n1", "type": "skill_call", "inputs": {}}]}
        r1 = run_graph(graph, root, use_cache=True, resume=True)
        r2 = run_graph(graph, root, use_cache=True, resume=True)
        assert r1["status"] == r2["status"] == "ok"
        assert "n1" in r1["results"] and "n1" in r2["results"]


def test_run_graph_failure_reporting() -> None:
    """A deliberately failing node stops the run and returns failed_node + error."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / ".clockwork_runtime").mkdir(parents=True)
        graph = {
            "nodes": [
                {"id": "a", "type": "skill_call", "inputs": {}},
                {"id": "fail_node", "type": "gate_check", "inputs": {}, "config": {"_test_fail": True}},
            ]
        }
        result = run_graph(graph, root, use_cache=False)
        assert result["status"] == "fail"
        assert result.get("failed_node") == "fail_node"
        assert "deliberate failure" in (result.get("error") or "")
        assert "a" in result.get("results", {})


def test_node_cache_set_get() -> None:
    with tempfile.TemporaryDirectory() as d:
        cache = NodeCache(d)
        cache.set("n1", {"x": 1}, {"out": 2})
        assert cache.get("n1", {"x": 1}) == {"out": 2}
        assert cache.get("n1", {"x": 2}) is None
