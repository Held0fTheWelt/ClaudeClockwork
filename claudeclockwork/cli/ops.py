"""Phase 55 — Operator toolkit: ops CLI namespace, quick actions, stable JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def run_ops_bundles(project_root: Path) -> dict[str, Any]:
    """Quick action: list imported bundles."""
    run_root = project_root / ".clockwork_runtime"
    index_path = run_root / "bundle_index.jsonl"
    bundles = []
    if index_path.is_file():
        for line in index_path.read_text(encoding="utf-8").strip().splitlines():
            if line.strip():
                try:
                    bundles.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return {"bundles": bundles, "count": len(bundles)}


def run_ops_plugins(project_root: Path) -> dict[str, Any]:
    """Quick action: plugin list from registry index."""
    from claudeclockwork.plugins.registry_index import build_index
    index = build_index(project_root)
    return {"plugins": index, "count": len(index)}


def run_ops_budget(project_root: Path) -> dict[str, Any]:
    """Quick action: current budget profile (stub)."""
    return {"budget_profile": "balanced", "source": "default"}


def run_ops_cache(project_root: Path) -> dict[str, Any]:
    """Quick action: cache stats (CAS/workgraph)."""
    run_root = project_root / ".clockwork_runtime"
    cas_objects = 0
    if (run_root / "cas" / "objects").is_dir():
        cas_objects = sum(1 for _ in (run_root / "cas" / "objects").rglob("*") if _.is_file())
    return {"cas_objects": cas_objects}
