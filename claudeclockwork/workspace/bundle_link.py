"""Phase 43 — Link evidence bundles across projects: store under project runtime, index metadata. No paths outside boundary."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claudeclockwork.workspace.bundle_import import import_bundle


def link_bundle(
    project_root: Path | str,
    bundle_path: Path | str,
    bundle_id: str = "",
    version: str = "1",
) -> dict[str, Any]:
    """Store bundle under project runtime; index metadata. No access to other repo paths."""
    result = import_bundle(project_root, bundle_path, bundle_id=bundle_id, version=version)
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    index = run_root / "bundle_links.jsonl"
    with open(index, "a", encoding="utf-8") as f:
        f.write(json.dumps({"bundle_id": result["bundle_id"], "version": result["version"]}) + "\n")
    return result