"""Phase 56 — Policy resolver: precedence (project > org > default), per-project budgets and plugin policy."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def resolve_policy(project_root: Path | str, org_config_path: Path | str | None = None) -> dict[str, Any]:
    """
    Resolve effective policy. Precedence: project .clockwork_policy.json > org config > defaults.
    Returns { budget_profile, max_plugins, plugin_allowlist_only, ... }.
    """
    root = Path(project_root).resolve()
    defaults = {"budget_profile": "balanced", "max_plugins": 0, "plugin_allowlist_only": False}
    if org_config_path and Path(org_config_path).is_file():
        import json
        try:
            data = json.loads(Path(org_config_path).read_text(encoding="utf-8"))
            defaults.update({k: v for k, v in data.items() if k in defaults})
        except (OSError, json.JSONDecodeError):
            pass
    project_policy = root / ".clockwork_policy.json"
    if project_policy.is_file():
        import json
        try:
            data = json.loads(project_policy.read_text(encoding="utf-8"))
            defaults.update({k: v for k, v in data.items() if k in defaults})
        except (OSError, json.JSONDecodeError):
            pass
    return defaults
