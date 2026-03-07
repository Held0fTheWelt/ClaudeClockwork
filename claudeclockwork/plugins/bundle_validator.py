"""Phase 47 — Plugin bundle validator: manifest, structure, no forbidden paths. Deterministic."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_MANIFEST = "plugin.json"
FORBIDDEN_PATHS = (".git", "__pycache__", ".env", "node_modules")


def validate_bundle(plugin_dir: Path | str) -> tuple[bool, list[str]]:
    """
    Validate a plugin bundle directory. Returns (ok, list of errors).
    - Must contain plugin.json
    - Manifest must be valid JSON with 'id'
    - No forbidden path segments
    """
    root = Path(plugin_dir).resolve()
    errors: list[str] = []

    if not root.is_dir():
        return False, ["not a directory"]

    manifest_path = root / REQUIRED_MANIFEST
    if not manifest_path.is_file():
        errors.append(f"missing {REQUIRED_MANIFEST}")

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        for part in rel.parts:
            if part in FORBIDDEN_PATHS:
                errors.append(f"forbidden path: {rel}")
                break

    if manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not data.get("id"):
                errors.append("manifest must contain 'id'")
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"invalid manifest: {e}")

    return len(errors) == 0, errors
