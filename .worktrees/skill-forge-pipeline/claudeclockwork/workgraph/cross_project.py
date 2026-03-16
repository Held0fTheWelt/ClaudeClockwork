"""Phase 58 — Cross-project graph: run with project-scoped handoff and incident bundles."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def run_cross_project_graph(
    graph: dict[str, Any],
    project_roots: dict[str, Path],
    default_project: str = "default",
) -> dict[str, Any]:
    """
    Run graph where nodes may have project_id. Handoff via bundle refs only.
    Failures produce project-scoped incident bundle (stub: return failed_node and project_id).
    """
    from claudeclockwork.workgraph.runner import run_graph
    current_project = default_project
    root = project_roots.get(current_project, Path("."))
    result = run_graph(graph, root, use_cache=True, resume=True)
    if result.get("status") == "fail" and result.get("failed_node"):
        result["incident_project_id"] = current_project
    return result
