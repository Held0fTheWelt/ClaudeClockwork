from pathlib import Path

from clockwork.tools.uml_shared import (
    render_component_plantuml,
    render_dependency_mermaid,
    scan_repository,
)


def make_mini_repo(tmp_path: Path) -> Path:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "alpha.py").write_text(
        "class Alpha:\n    def run(self):\n        return 1\n", encoding="utf-8"
    )
    (pkg / "beta.py").write_text(
        "from pkg.alpha import Alpha\n\n\ndef use():\n    return Alpha().run()\n",
        encoding="utf-8",
    )
    return tmp_path


def test_scan_finds_modules_and_classes(tmp_path):
    scan = scan_repository(make_mini_repo(tmp_path))
    module_ids = {m.module_id for m in scan.modules}
    assert "pkg.alpha" in module_ids
    assert "pkg.beta" in module_ids
    assert scan.class_count >= 1


def test_renderers_produce_diagram_sources(tmp_path):
    scan = scan_repository(make_mini_repo(tmp_path))
    puml = render_component_plantuml("t", scan.modules)
    mmd = render_dependency_mermaid("t", scan.modules)
    assert puml.startswith("@startuml")
    assert "flowchart" in mmd or "graph" in mmd
