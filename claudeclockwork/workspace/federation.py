"""Phase 43 — Federated workspace config: multiple roots, active workspace + project. Stable selection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_federation_config(workspace_root: Path | str) -> dict[str, Any]:
    """Load federation config (workspaces list, active workspace, active project)."""
    root = Path(workspace_root).resolve()
    for name in ["federation.json", "workspace.json"]:
        p = root / name
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
    return {"workspaces": [], "active_workspace": None, "active_project": None}


def set_active(workspace_root: Path | str, workspace_id: str | None = None, project_id: str | None = None) -> None:
    """Persist active workspace and/or project. Stable."""
    root = Path(workspace_root).resolve()
    cfg = load_federation_config(root)
    if workspace_id is not None:
        cfg["active_workspace"] = workspace_id
    if project_id is not None:
        cfg["active_project"] = project_id
    (root / "federation.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")