"""Phase 61 — Marketplace UX: search, info, install, update, uninstall. Local registry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def plugin_search(project_root: Path, query: str = "") -> dict[str, Any]:
    """Search local registry index. Returns list of plugins (id, compatible, certification_tier)."""
    from claudeclockwork.plugins.registry_index import build_index
    index = build_index(project_root)
    if query:
        index = [p for p in index if query.lower() in (p.get("id") or "").lower()]
    return {"plugins": index, "query": query}


def plugin_info(project_root: Path, plugin_id: str) -> dict[str, Any]:
    """Info for one plugin from registry."""
    from claudeclockwork.plugins.registry_index import build_index
    index = build_index(project_root)
    for p in index:
        if p.get("id") == plugin_id:
            return {"plugin": p}
    return {"plugin": None, "error": "not_found"}


def plugin_install(project_root: Path, plugin_id: str, bundle_path: Path | str) -> dict[str, Any]:
    """Validate bundle (hash/sign), then copy to plugins dir. Returns { ok, error? }."""
    from claudeclockwork.plugins.bundle_validator import validate_bundle
    root = Path(project_root).resolve()
    bundle = Path(bundle_path).resolve()
    ok, errs = validate_bundle(bundle)
    if not ok:
        return {"ok": False, "errors": errs}
    dest = root / "plugins" / plugin_id
    dest.mkdir(parents=True, exist_ok=True)
    import shutil
    for f in bundle.iterdir():
        if f.is_file():
            shutil.copy2(f, dest / f.name)
        elif f.is_dir() and f.name != ".git":
            shutil.copytree(f, dest / f.name, dirs_exist_ok=True)
    return {"ok": True, "plugin_id": plugin_id, "dest": str(dest)}


def plugin_update(project_root: Path, plugin_id: str, bundle_path: Path | str) -> dict[str, Any]:
    """Same as install; overwrites existing. Validate before copy."""
    return plugin_install(project_root, plugin_id, bundle_path)


def plugin_uninstall(project_root: Path, plugin_id: str) -> dict[str, Any]:
    """Remove plugin dir. Returns { ok }."""
    root = Path(project_root).resolve()
    for base in ["plugins", ".clockwork_plugins"]:
        d = root / base / plugin_id
        if d.is_dir():
            import shutil
            shutil.rmtree(d, ignore_errors=True)
            return {"ok": True, "plugin_id": plugin_id}
    return {"ok": True, "plugin_id": plugin_id}
