"""Phase 37 — Import existing repo into workspace config."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def import_project(
    repo_path: Path | str,
    workspace_root: Path | str,
    project_id: str = "",
    runtime_root_rel: str = ".clockwork_runtime",
) -> dict[str, Any]:
    """Detect repo root, propose runtime root, add to workspace config. Stable config entries."""
    repo = Path(repo_path).resolve()
    ws_root = Path(workspace_root).resolve()
    if not repo.is_dir():
        return {"status": "error", "error": "not_a_directory"}
    pid = project_id or repo.name
    config_path = ws_root / "workspace.json"
    import json
    if config_path.is_file():
        data = json.loads(config_path.read_text(encoding="utf-8"))
    else:
        data = {"projects": [], "active_project": None}
    for p in data.get("projects", []):
        if p.get("id") == pid:
            return {"status": "ok", "project_id": pid, "already_present": True}
    try:
        rel = repo.relative_to(ws_root)
    except ValueError:
        rel = repo.name
    data.setdefault("projects", []).append({
        "id": pid,
        "path": str(repo),
        "runtime_root": runtime_root_rel,
    })
    data["active_project"] = pid
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"status": "ok", "project_id": pid, "path": str(repo)}
