"""Phase 42 — Drilldown: node/worker/tool timeline. Deterministic, repo-local paths."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def drilldown_node(project_root: Path | str, node_id: str) -> dict[str, Any]:
    """Timeline + key artifacts for node. Repo-local paths."""
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    return {"node_id": node_id, "timeline": [], "artifacts": [str(run_root / "workgraph_cache")]}


def drilldown_worker(project_root: Path | str, worker_id: str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    return {"worker_id": worker_id, "timeline": [], "artifacts": [str(run_root / "worker_jobs")]}


def drilldown_tool(project_root: Path | str, tool_id: str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    return {"tool_id": tool_id, "timeline": [], "artifacts": []}