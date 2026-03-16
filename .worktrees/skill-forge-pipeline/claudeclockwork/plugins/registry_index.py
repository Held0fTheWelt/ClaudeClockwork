"""Phase 40 — Local plugin registry index: status, compat, last test result. Deterministic."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claudeclockwork.plugins.loader import PluginLoader
from claudeclockwork.plugins.signing import load_allowlist, content_hash_plugin, is_allowlisted
from claudeclockwork.plugins.compat import is_compatible


def build_index(project_root: Path | str, clockwork_version: str = "17.0", strict: bool = False) -> list[dict[str, Any]]:
    """Build registry index: each plugin has allowed, compatibility, last_test (stub). Stable order."""
    root = Path(project_root).resolve()
    loader = PluginLoader(root, clockwork_version)
    allowlist = load_allowlist(root)
    index: list[dict[str, Any]] = []
    for base in ["plugins", ".clockwork_plugins"]:
        plug_root = root / base
        if not plug_root.is_dir():
            continue
        for manifest_file in sorted(plug_root.glob("*/plugin.json")):
            try:
                data = json.loads(manifest_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            pid = data.get("id") or manifest_file.parent.name
            plug_dir = manifest_file.parent
            allowed, _ = is_allowlisted(pid, plug_dir, root, strict=strict)
            compat, _ = is_compatible(data.get("clockwork_compat"), clockwork_version)
            cert = {"tier": "experimental"}
            try:
                from claudeclockwork.plugins.certification import run_certification
                cert = run_certification(plug_dir, root)
            except Exception:
                pass
            index.append({
                "id": pid,
                "allowed": allowed,
                "compatible": compat,
                "last_test": None,
                "certification_tier": cert.get("tier", "experimental"),
            })
    return index
