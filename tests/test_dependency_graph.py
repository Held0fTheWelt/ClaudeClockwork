"""Phase 57 — Dependency graph and impact analysis."""
from pathlib import Path

from claudeclockwork.workspace.dependency_graph import build_dependency_graph, impact_analysis


def test_graph_deterministic(tmp_path: Path) -> None:
    (tmp_path / ".clockwork_runtime").mkdir(parents=True)
    (tmp_path / ".clockwork_runtime" / "bundle_index.jsonl").write_text(
        '{"bundle_id": "b1"}\n', encoding="utf-8"
    )
    g = build_dependency_graph(tmp_path)
    assert "nodes" in g and "edges" in g
    assert any(n["id"] == "root" for n in g["nodes"])
    assert any(n["id"] == "bundle:b1" for n in g["nodes"])


def test_impact_analysis() -> None:
    g = {"nodes": [], "edges": [{"from": "root", "to": "bundle:a"}]}
    assert impact_analysis(g, "root") == ["bundle:a"]
