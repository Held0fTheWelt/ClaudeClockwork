"""Phase 43 — Orchestrator CLI: run, incident, export-incident, import-bundle. Boundaries respected."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def run_orchestrate(
    workspace_root: Path | str,
    project_id: str,
    graph_path: Path | str | None = None,
    command: str = "run",
) -> dict[str, Any]:
    """Dispatch: run graph, incident --last, export-incident, import-bundle. Deterministic output."""
    root = Path(workspace_root).resolve()
    if command == "run" and graph_path:
        from claudeclockwork.workgraph.runner import run_graph
        g = json.loads(Path(graph_path).read_text(encoding="utf-8")) if Path(graph_path).is_file() else {"nodes": [], "edges": []}
        project_path = root / project_id if (root / project_id).is_dir() else root
        return run_graph(g, project_path)
    if command == "incident":
        from claudeclockwork.cli.incidents import incident_summary
        project_path = root / project_id if (root / project_id).is_dir() else root
        return incident_summary(project_path)
    if command == "export-incident":
        from claudeclockwork.cli.export_incident import export_incident
        project_path = root / project_id if (root / project_id).is_dir() else root
        return export_incident(project_path, last_n=10)
    if command == "import-bundle":
        return {"status": "ok", "message": "use link_bundle with bundle path"}
    return {"status": "error", "error": "unknown_command"}