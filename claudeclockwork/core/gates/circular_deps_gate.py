"""Phase 52 — Circular dependency gate: fail if import cycle detected."""
from __future__ import annotations

import sys
from pathlib import Path


def _project_root() -> Path:
    p = Path(__file__).resolve()
    for _ in range(5):
        if (p / "claudeclockwork" / "__init__.py").is_file():
            return p
        p = p.parent
    return Path.cwd()


def run_circular_deps_gate(project_root: Path | str | None = None) -> dict:
    """
    Try importing main packages; cycles cause import error. Returns { pass, errors }.
    """
    root = Path(project_root).resolve() if project_root else _project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    errors = []
    packages = ["claudeclockwork", "claudeclockwork.core", "claudeclockwork.cli", "claudeclockwork.cas",
                "claudeclockwork.workgraph", "claudeclockwork.plugins", "claudeclockwork.scheduler",
                "claudeclockwork.optimizer", "claudeclockwork.workers", "claudeclockwork.workspace"]
    for pkg in packages:
        try:
            __import__(pkg)
        except Exception as e:
            errors.append(f"{pkg}: {e}")
    return {"pass": len(errors) == 0, "errors": errors}
