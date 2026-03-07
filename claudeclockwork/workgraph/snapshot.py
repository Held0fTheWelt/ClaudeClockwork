"""Phase 39 — Work graph rollback: snapshot before run, restore on failure, write rollback evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claudeclockwork.core.snapshot.simple_snapshot import create_snapshot, restore_snapshot


def snapshot_before_graph(project_root: Path | str, paths: list[str] | None = None) -> dict[str, Any]:
    """Snapshot state before graph run. Default paths: workgraph_cache, worker_jobs."""
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    paths = paths or ["workgraph_cache", "worker_jobs"]
    snap_dir = run_root / "rollback_snapshot"
    out = create_snapshot(run_root, paths, snap_dir)
    out["rollback_marker"] = str(snap_dir / "marker.json")
    (snap_dir / "marker.json").write_text(json.dumps({"phase": "pre_run"}) + "\n", encoding="utf-8")
    return out


def restore_on_failure(project_root: Path | str, snapshot_result: dict[str, Any]) -> None:
    """Restore from snapshot into runtime root. Write rollback evidence."""
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    snap_dir = snapshot_result.get("snapshot_dir")
    if not snap_dir:
        return
    restore_snapshot(run_root, snap_dir)
    evidence = run_root / "rollback_evidence.jsonl"
    with open(evidence, "a", encoding="utf-8") as f:
        f.write(json.dumps({"event": "restore", "snapshot_dir": snap_dir}) + "\n")