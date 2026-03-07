"""Phase 27 — Simple file snapshot for rollback (copy dirs, restore on failure)."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


def create_snapshot(
    project_root: Path | str,
    paths: list[str],
    snapshot_dir: Path | str,
) -> dict[str, Any]:
    """Copy given paths into snapshot_dir. Returns manifest of what was copied."""
    root = Path(project_root).resolve()
    snap = Path(snapshot_dir).resolve()
    snap.mkdir(parents=True, exist_ok=True)
    manifest: list[str] = []
    for rel in paths:
        src = root / rel
        if not src.exists():
            continue
        dst = snap / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, dst)
            manifest.append(rel)
        elif src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            manifest.append(rel + "/")
    return {"paths": manifest, "snapshot_dir": str(snap)}


def restore_snapshot(
    project_root: Path | str,
    snapshot_dir: Path | str,
) -> None:
    """Restore from snapshot_dir into project_root (overwrite)."""
    root = Path(project_root).resolve()
    snap = Path(snapshot_dir).resolve()
    if not snap.is_dir():
        return
    for item in snap.rglob("*"):
        if item.is_file():
            rel = item.relative_to(snap)
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst)
