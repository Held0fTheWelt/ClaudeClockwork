"""Phase 40 — Plugin hash allowlist: deterministic, repo-local; strict mode rejects unallowlisted."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def content_hash_plugin(plugin_dir: Path | str) -> str:
    """Hash plugin dir (manifest + key files). Deterministic."""
    d = Path(plugin_dir).resolve()
    h = hashlib.sha256()
    for f in sorted(d.rglob("*")):
        if f.is_file() and ".git" not in f.parts:
            h.update(f.read_bytes())
    return h.hexdigest()[:32]


def load_allowlist(project_root: Path | str) -> dict[str, str]:
    """Load plugin id -> hash from allowlist file."""
    root = Path(project_root).resolve()
    for name in [".clockwork_plugins_allowlist.json", "plugins_allowlist.json"]:
        p = root / name
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
    return {}


def is_allowlisted(plugin_id: str, plugin_dir: Path | str, project_root: Path | str, strict: bool = False) -> tuple[bool, str]:
    """Return (allowed, reason). In strict mode, hash must be in allowlist."""
    allowlist = load_allowlist(project_root)
    if not strict:
        return True, ""
    h = content_hash_plugin(plugin_dir)
    if allowlist.get(plugin_id) != h:
        return False, "hash_not_allowlisted"
    return True, ""
