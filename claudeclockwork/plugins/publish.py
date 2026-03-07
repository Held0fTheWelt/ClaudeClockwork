"""Phase 47 — Publish workflow: test (validate) → sign/hash → index update. Deterministic."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claudeclockwork.plugins.bundle_validator import validate_bundle
from claudeclockwork.plugins.signing import content_hash_plugin
from claudeclockwork.plugins.registry_index import build_index


def run_publish_workflow(
    plugin_dir: Path | str,
    project_root: Path | str,
    clockwork_version: str = "17.0",
    update_allowlist: bool = False,
) -> dict[str, Any]:
    """
    Test (validate bundle) → compute hash → optionally update allowlist → rebuild index.
    Returns { "ok": bool, "errors": [], "hash": str|None, "index_updated": bool }.
    """
    root = Path(project_root).resolve()
    plug_dir = Path(plugin_dir).resolve()
    errors: list[str] = []

    ok, val_errors = validate_bundle(plug_dir)
    if not ok:
        return {"ok": False, "errors": val_errors, "hash": None, "index_updated": False}

    h = content_hash_plugin(plug_dir)
    manifest_path = plug_dir / "plugin.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    pid = data.get("id", plug_dir.name)

    if update_allowlist:
        allowlist_path = root / ".clockwork_plugins_allowlist.json"
        allowlist: dict[str, str] = {}
        if allowlist_path.is_file():
            try:
                allowlist = json.loads(allowlist_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        allowlist[pid] = h
        allowlist_path.write_text(json.dumps(allowlist, indent=2) + "\n", encoding="utf-8")

    index = build_index(root, clockwork_version=clockwork_version)
    index_path = root / ".clockwork_runtime" / "registry_index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    return {"ok": True, "errors": [], "hash": h, "index_updated": True}
