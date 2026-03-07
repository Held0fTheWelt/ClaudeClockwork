"""Phase 41 — Cache-aware planner: prefer nodes with existing CAS inputs/outputs."""
from __future__ import annotations

from typing import Any


def plan_order(
    nodes: list[dict[str, Any]],
    cas_available_hashes: set[str],
) -> list[str]:
    """Return node execution order to maximize cache hits. Nodes with all inputs in CAS first."""
    node_ids = [n.get("id", "") for n in nodes]
    by_id = {n.get("id"): n for n in nodes}
    ready = []
    for nid in node_ids:
        refs = (by_id.get(nid) or {}).get("input_artifact_refs") or []
        if all(r in cas_available_hashes for r in refs):
            ready.append(nid)
    rest = [n for n in node_ids if n not in ready]
    return sorted(ready) + sorted(rest)