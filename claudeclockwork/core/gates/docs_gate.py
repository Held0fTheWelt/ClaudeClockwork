"""
Phase 45 — Docs gate: link integrity and required docs presence.

Fails when required docs are missing or INDEX.md contains broken internal links.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_DOCS = [
    "Docs/INDEX.md",
    "Docs/troubleshooting.md",
    "Docs/failure_taxonomy.md",
    "Docs/install.md",
    "Docs/runbooks/install_upgrade.md",
    "Docs/runbooks/workers_cas.md",
    "Docs/runbooks/work_graphs.md",
    "Docs/runbooks/plugins.md",
    "Docs/runbooks/incidents_exports.md",
]


def _project_root() -> Path:
    p = Path(__file__).resolve()
    for _ in range(5):
        if (p / "claudeclockwork" / "__init__.py").is_file():
            return p
        p = p.parent
    return Path.cwd()


def _collect_internal_links(docs_root: Path, index_path: Path) -> list[tuple[str, str]]:
    """Return list of (anchor_text, href) for links like [text](path)."""
    if not index_path.is_file():
        return []
    text = index_path.read_text(encoding="utf-8")
    # Match [text](path) where path is relative (no scheme, no //)
    pattern = re.compile(r"\[([^\]]*)\]\(([^)#\s]+)\)")
    return pattern.findall(text)


def run_docs_gate(project_root: Path | str | None = None) -> dict:
    """
    Run docs gate. Returns dict: pass (bool), errors (list).
    Checks required docs exist and INDEX.md internal links resolve.
    """
    root = Path(project_root).resolve() if project_root else _project_root()
    errors = []

    for rel in REQUIRED_DOCS:
        path = root / Path(rel)
        if not path.is_file():
            errors.append(f"Missing required doc: {rel}")

    index_path = root / "Docs" / "INDEX.md"
    for _text, href in _collect_internal_links(root / "Docs", index_path):
        if href.startswith("http") or "://" in href:
            continue
        target = (index_path.parent / href).resolve()
        if not target.exists():
            errors.append(f"Broken link in INDEX.md: {href}")

    return {"pass": len(errors) == 0, "errors": errors}


def main() -> int:
    result = run_docs_gate()
    if not result["pass"]:
        for e in result["errors"]:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
