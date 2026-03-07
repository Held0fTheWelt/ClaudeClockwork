"""Phase 33 — Import redacted evidence bundle into project as versioned artifact (no hard paths)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def import_bundle(
    project_root: Path | str,
    bundle_path: Path | str,
    bundle_id: str = "",
    version: str = "1",
) -> dict[str, Any]:
    """Import a redacted bundle into project runtime; index by bundle_id/version. Does not modify other repos."""
    root = Path(project_root).resolve()
    bundle_path = Path(bundle_path).resolve()
    run_root = root / ".clockwork_runtime"
    imports_dir = run_root / "imported_bundles"
    imports_dir.mkdir(parents=True, exist_ok=True)
    bid = bundle_id or bundle_path.stem
    dest = imports_dir / f"{bid}_{version}"
    dest.mkdir(parents=True, exist_ok=True)
    if bundle_path.is_file() and bundle_path.suffix == ".zip":
        import zipfile
        with zipfile.ZipFile(bundle_path, "r") as z:
            z.extractall(dest)
    elif bundle_path.is_dir():
        import shutil
        for f in bundle_path.iterdir():
            shutil.copy2(f, dest / f.name) if f.is_file() else shutil.copytree(f, dest / f.name, dirs_exist_ok=True)
    index_path = run_root / "bundle_index.jsonl"
    record = {"bundle_id": bid, "version": version, "path": str(dest.relative_to(run_root))}
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return {"bundle_id": bid, "version": version, "dest": str(dest)}
