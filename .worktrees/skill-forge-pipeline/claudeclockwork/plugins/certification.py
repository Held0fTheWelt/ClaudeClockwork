"""Phase 59 — Plugin certification: assign tier (experimental/verified/certified). Deterministic."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.plugins.bundle_validator import validate_bundle
from claudeclockwork.plugins.signing import is_allowlisted


def run_certification(plugin_dir: Path | str, project_root: Path | str) -> dict[str, Any]:
    """Assign tier: certified if valid + allowlisted, verified if valid, else experimental."""
    import json
    plug_dir = Path(plugin_dir).resolve()
    root = Path(project_root).resolve()
    ok, errs = validate_bundle(plug_dir)
    if not ok:
        return {"tier": "experimental", "errors": errs}
    manifest_path = plug_dir / "plugin.json"
    pid = plug_dir.name
    if manifest_path.is_file():
        try:
            pid = json.loads(manifest_path.read_text(encoding="utf-8")).get("id", pid)
        except (OSError, json.JSONDecodeError):
            pass
    allowed, _ = is_allowlisted(pid, plug_dir, root, strict=False)
    allowlist_path = root / ".clockwork_plugins_allowlist.json"
    if allowed and allowlist_path.is_file():
        allowlist = json.loads(allowlist_path.read_text(encoding="utf-8"))
        if allowlist.get(pid):
            return {"tier": "certified"}
    return {"tier": "verified"}
