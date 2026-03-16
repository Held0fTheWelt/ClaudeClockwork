"""Phase 37 — Workspace dashboard CLI: active project, runtime root, last runs, top errors."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.workspace.config import load_workspace_config, get_project_runtime_root


def run_dashboard(workspace_root: Path | str, last_n: int = 5) -> dict[str, Any]:
    """Return dashboard data: active_project, runtime_root, last_n runs, top_errors (stub). Deterministic ordering."""
    root = Path(workspace_root).resolve()
    cfg = load_workspace_config(root)
    active = cfg.get("active_project")
    runtime_root = str(get_project_runtime_root(root, active)) if active else None
    runs: list[dict] = []
    telemetry_path = Path(runtime_root or root) / ".clockwork_runtime" / "telemetry" / "events.jsonl"
    if telemetry_path.is_file():
        lines = telemetry_path.read_text(encoding="utf-8").strip().split("\n")
        for line in reversed(lines[-last_n:] if lines else []):
            try:
                import json
                runs.append(json.loads(line))
            except Exception:
                pass
    return {
        "active_project": active,
        "runtime_root": runtime_root,
        "last_runs": runs,
        "top_errors": [],
        "version": "0.1.0",
    }
