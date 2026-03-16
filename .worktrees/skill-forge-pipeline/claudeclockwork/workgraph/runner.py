"""Phase 30 — Deterministic DAG runner with topological order and cache."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.workgraph.cache import NodeCache


def _topological_order(nodes: list[dict], edges: list[dict]) -> list[str]:
    """Stable topological order (by node id when no edges)."""
    if not edges:
        return sorted([n["id"] for n in nodes])
    # Build in-degree and adjacency
    ids = {n["id"] for n in nodes}
    in_deg = {i: 0 for i in ids}
    adj: dict[str, list[str]] = {i: [] for i in ids}
    for e in edges:
        f, t = e.get("from_node"), e.get("to_node")
        if f in ids and t in ids:
            adj[f].append(t)
            in_deg[t] += 1
    order: list[str] = []
    stack = sorted([i for i in ids if in_deg[i] == 0])
    while stack:
        u = stack.pop(0)
        order.append(u)
        for v in adj[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                stack.append(v)
                stack.sort()
    return order if len(order) == len(ids) else sorted(ids)


def run_graph(
    graph: dict[str, Any],
    project_root: Path | str,
    use_cache: bool = True,
    resume: bool = True,
) -> dict[str, Any]:
    """
    Run graph nodes in topological order. Cache hits skip execution.
    Returns { "status": "ok"|"fail", "results": {}, "failed_node": str|None, "error": str|None }.
    """
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    cache = NodeCache(run_root) if use_cache else None
    nodes = {n["id"]: n for n in graph.get("nodes", [])}
    edges = graph.get("edges", [])
    order = _topological_order(list(nodes.values()), edges)
    results: dict[str, Any] = {}
    for node_id in order:
        node = nodes.get(node_id)
        if not node:
            continue
        inputs = node.get("inputs", {})
        if cache and resume:
            cached = cache.get(node_id, inputs)
            if cached is not None:
                results[node_id] = cached
                continue
        # Minimal execution: no real skill/gate call, just stub output
        try:
            if node.get("config", {}).get("_test_fail"):
                raise RuntimeError("deliberate failure")
            out = {"node_id": node_id, "status": "ok", "output": {}}
            results[node_id] = out
            if cache:
                cache.set(node_id, inputs, out)
        except Exception as e:
            return {
                "status": "fail",
                "results": results,
                "failed_node": node_id,
                "error": str(e),
            }
    return {"status": "ok", "results": results, "failed_node": None, "error": None}
