"""Phase 57 — Cross-repo dependency graph (metadata only): bundles, plugins, versions."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def build_dependency_graph(project_root: Path | str) -> dict[str, Any]:
    """Build deterministic graph: nodes = projects/bundles/plugins, edges = depends_on. No hard paths."""
    root = Path(project_root).resolve()
    nodes = [{"id": "root", "type": "project"}]
    edges = []
    run_root = root / ".clockwork_runtime"
    if (run_root / "bundle_index.jsonl").is_file():
        import json
        for line in (run_root / "bundle_index.jsonl").read_text(encoding="utf-8").strip().splitlines():
            if not line:
                continue
            try:
                rec = json.loads(line)
                bid = rec.get("bundle_id", "?")
                nodes.append({"id": f"bundle:{bid}", "type": "bundle"})
                edges.append({"from": "root", "to": f"bundle:{bid}"})
            except json.JSONDecodeError:
                pass
    return {"nodes": nodes, "edges": edges}


def impact_analysis(graph: dict[str, Any], node_id: str) -> list[str]:
    """Return list of node ids that depend on node_id (downstream impact)."""
    edges = graph.get("edges", [])
    return [e["to"] for e in edges if e.get("from") == node_id]
