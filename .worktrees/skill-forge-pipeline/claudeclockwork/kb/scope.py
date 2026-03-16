"""Phase 38 — Index scope: include/exclude paths; respect boundaries."""
from __future__ import annotations

from pathlib import Path

INCLUDE_GLOBS = [
    "Docs/**/*",
    "mvps/**/*",
    ".claude/skills/**/manifest.json",
    ".claude/contracts/**/*",
]
EXCLUDE_DIRS = frozenset({".clockwork_runtime", "__pycache__", ".git", "venv", ".venv", "dist", "build", ".eggs"})


def in_scope(path: Path, project_root: Path) -> bool:
    """True if path is under project_root and matches include rules and not excluded."""
    try:
        rel = path.resolve().relative_to(Path(project_root).resolve())
    except ValueError:
        return False
    parts = rel.parts
    for d in EXCLUDE_DIRS:
        if d in parts:
            return False
    s = str(rel).replace("\\", "/")
    for g in INCLUDE_GLOBS:
        if _glob_matches(g, s):
            return True
    return False


def _glob_matches(pattern: str, path: str) -> bool:
    """Prefix match for include globs (Docs/, mvps/, .claude/...)."""
    path = path.replace("\\", "/")
    if pattern.endswith("/**/*"):
        prefix = pattern[:-5]
        return path == prefix or path.startswith(prefix + "/")
    return path.startswith(pattern.replace("**/*", "").rstrip("/") + "/") or path == pattern.replace("**/*", "").rstrip("/")
