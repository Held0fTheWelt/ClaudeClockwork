from pathlib import Path

from clockwork.tools.how_it_works_shared import build_how_it_works_payload
from clockwork.tools.uml_review_shared import build_review_context, write_review_site
from clockwork.tools.uml_shared import scan_repository


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


def test_review_context_covers_scanned_modules(tmp_path):
    scan = scan_repository(make_mini_repo(tmp_path))
    payload = build_review_context(scan)
    assert payload["modules"], "expected module entries"
    assert payload["directories"], "expected directory entries"


def test_review_site_and_guides_written(tmp_path):
    repo = make_mini_repo(tmp_path / "repo")
    scan = scan_repository(repo)
    context = build_review_context(scan)
    guide = build_how_it_works_payload(scan, context_payload=context, repo_root=repo)
    out = tmp_path / "site"
    write_review_site(out, context, guide_payload=guide)
    assert (out / "index.html").exists()
    assert (out / "modules").is_dir()
