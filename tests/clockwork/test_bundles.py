import json
from pathlib import Path

import pytest

from clockwork.tools import bundles
from clockwork.tools.uml_shared import UmlSkillError


def make_mini_repo(tmp_path: Path) -> Path:
    pkg = tmp_path / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "alpha.py").write_text(
        "class Alpha:\n    def run(self):\n        return 1\n", encoding="utf-8"
    )
    (pkg / "beta.py").write_text(
        "from pkg.alpha import Alpha\n\n\ndef use():\n    return Alpha().run()\n",
        encoding="utf-8",
    )
    return tmp_path


def test_scope_catalog_writes_json_and_md(tmp_path):
    repo = make_mini_repo(tmp_path / "repo")
    out = tmp_path / "out"
    result = bundles.build_scope_catalog(repo, output_dir=out)
    payload = json.loads((out / "uml_scope_catalog.json").read_text(encoding="utf-8"))
    assert payload["summary"]["module_count"] >= 2
    assert (out / "uml_scope_catalog.md").exists()
    assert result["module_count"] >= 2


def test_repo_bundle_writes_overviews(tmp_path):
    repo = make_mini_repo(tmp_path / "repo")
    out = tmp_path / "out"
    result = bundles.build_repo_bundle(repo, output_dir=out)
    assert (out / "repo_component_overview.puml").exists()
    assert (out / "repo_dependency_overview.mmd").exists()
    assert (out / "README.md").exists()
    assert result["output_dir"] == str(out.resolve())


def test_focus_bundle_rejects_repo_scope(tmp_path):
    repo = make_mini_repo(tmp_path / "repo")
    with pytest.raises(UmlSkillError):
        bundles.build_focus_bundle(repo, scope_kind="repo", target="x")


def test_generate_diagrams_repo_scope(tmp_path):
    repo = make_mini_repo(tmp_path / "repo")
    out = tmp_path / "out"
    result = bundles.generate_diagrams(repo, output_dir=out)
    assert result["scope"]["module_count"] >= 2
    assert (out / "README.md").exists()


def test_review_and_guide_bundles(tmp_path):
    repo = make_mini_repo(tmp_path / "repo")
    ctx = bundles.build_review_context_bundle(repo, output_dir=tmp_path / "ctx")
    assert ctx["module_count"] >= 2
    site = bundles.build_review_site_bundle(repo, output_dir=tmp_path / "site")
    assert "output_dir" in site
    guide = bundles.build_how_it_works_bundle(repo, output_dir=tmp_path / "guide")
    assert "output_dir" in guide
