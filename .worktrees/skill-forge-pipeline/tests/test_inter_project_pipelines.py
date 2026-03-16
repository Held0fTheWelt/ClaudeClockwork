"""Phase 58 — Inter-project pipelines: handoff and boundaries."""
from pathlib import Path

from claudeclockwork.workgraph.cross_project import run_cross_project_graph


def test_cross_project_handoff_boundaries(tmp_path: Path) -> None:
    roots = {"default": tmp_path}
    graph = {"nodes": [{"id": "a", "type": "skill_call"}], "edges": []}
    result = run_cross_project_graph(graph, roots)
    assert result.get("status") == "ok"


def test_failure_produces_project_scoped_incident(tmp_path: Path) -> None:
    roots = {"default": tmp_path}
    graph = {"nodes": [{"id": "fail", "type": "skill_call", "config": {"_test_fail": True}}], "edges": []}
    result = run_cross_project_graph(graph, roots)
    assert result.get("status") == "fail"
    assert result.get("incident_project_id") == "default"
