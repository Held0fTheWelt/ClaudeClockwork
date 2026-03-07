"""Phase 37 — Create new project from template (clockwork new)."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


def create_from_template(
    template_id: str,
    dest_dir: Path | str,
    project_id: str = "",
    workspace_config_path: Path | str | None = None,
) -> dict[str, Any]:
    """Create project skeleton from template. Fails safely if dest exists and has content."""
    dest = Path(dest_dir).resolve()
    if dest.exists() and any(dest.iterdir()):
        return {"status": "error", "error": "destination_not_empty", "message": "Directory exists and is not empty; use a new path or remove contents."}
    template = TEMPLATES_DIR / template_id
    if not template.is_dir():
        return {"status": "error", "error": "unknown_template", "message": f"Template {template_id} not found."}
    shutil.copytree(template, dest, dirs_exist_ok=False)
    pid = project_id or dest.name
    if workspace_config_path:
        _add_workspace_entry(Path(workspace_config_path), pid, str(dest))
    return {"status": "ok", "project_id": pid, "path": str(dest)}


def _add_workspace_entry(config_path: Path, project_id: str, project_path: str) -> None:
    import json
    config_path = config_path.resolve()
    if config_path.is_file():
        data = json.loads(config_path.read_text(encoding="utf-8"))
    else:
        data = {"projects": [], "active_project": None}
    data.setdefault("projects", [])
    for p in data["projects"]:
        if p.get("id") == project_id:
            return
    data["projects"].append({"id": project_id, "path": project_path, "runtime_root": ".clockwork_runtime"})
    data["active_project"] = project_id
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
