"""Phase 36 — Node cache key + CAS: reuse when inputs/params match."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.cas.store import put, get
from claudeclockwork.workgraph.cache import NodeCache
from claudeclockwork.workgraph.runner import run_graph


def test_node_reuse_via_cache() -> None:
    """Re-running same node reuses cached output (cache key = node_id + inputs)."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        graph = {"nodes": [{"id": "n1", "inputs": {"x": 1}, "config": {}}], "edges": []}
        r1 = run_graph(graph, root, use_cache=True, resume=True)
        r2 = run_graph(graph, root, use_cache=True, resume=True)
        assert r1["status"] == r2["status"] == "ok"
        assert r1["results"]["n1"] == r2["results"]["n1"]


def test_cas_ref_reuse() -> None:
    """Output stored as CAS ref can be retrieved (simulated reuse)."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        out_data = b'{"status":"ok"}'
        h = put(root, out_data, metadata={"producer": "node_1"})
        retrieved = get(root, h)
        assert retrieved == out_data