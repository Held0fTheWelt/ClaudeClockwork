"""Phase 33 — Workspace config: projects, runtime roots, discovery."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_workspace_config(workspace_root: Path | str) -> dict[str, Any]:
    """Load workspace config (projects list). Deterministic."""
    root = Path(workspace_root).resolve()
    for name in ["workspace.json", ".clockwork_workspace.json"]:
        p = root / name
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
    return {"projects": [], "active_project": None}


def get_project_runtime_root(workspace_root: Path | str, project_id: str) -> Path | None:
    """Return runtime root path for project. None if not found."""
    cfg = load_workspace_config(workspace_root)
    for p in cfg.get("projects", []):
        if p.get("id") == project_id:
            root = Path(workspace_root).resolve()
            rel = p.get("runtime_root", f".clockwork_runtime_{project_id}")
            return (root / rel).resolve()
    return None
