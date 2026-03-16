#!/usr/bin/env python3
"""
Phase 27 — Batch conversion run: snapshot → convert → validate → rollback on failure.

Usage:
  python scripts/adapter_batch_run.py [--dry-run] [--batch-size N]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Import snapshot from package
try:
    from claudeclockwork.core.snapshot import create_snapshot, restore_snapshot
except ImportError:
    create_snapshot = restore_snapshot = None  # type: ignore[misc, assignment]


def run_batch_plan(root: Path, batch_size: int) -> list[str]:
    r = subprocess.run(
        [sys.executable, "scripts/adapter_batch_plan.py", "--batch-size", str(batch_size)],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return []
    return json.loads(r.stdout) if r.stdout.strip() else []


def run_gates(root: Path) -> bool:
    """Run qa_gate (or pytest). Return True if pass."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line", "-x"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Adapter batch run with rollback (Phase 27).")
    ap.add_argument("--dry-run", action="store_true", help="Only plan, do not convert")
    ap.add_argument("--batch-size", type=int, default=50)
    args = ap.parse_args()
    root = Path.cwd()
    run_root = root / ".clockwork_runtime" / "adapter_batch"
    run_root.mkdir(parents=True, exist_ok=True)

    batch = run_batch_plan(root, args.batch_size)
    report = {"converted": [], "failures": [], "rollback": False, "validation_pass": None}

    if not batch:
        report["message"] = "No adapter skills to convert (batch empty)."
        (run_root / "conversion_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(report["message"])
        return 0

    if args.dry_run:
        report["planned"] = batch
        (run_root / "conversion_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("Dry run: would convert", batch)
        return 0

    if create_snapshot is None or restore_snapshot is None:
        print("Snapshot module unavailable.", file=sys.stderr)
        return 1

    # Snapshot affected skill dirs
    paths_to_snap = [f".claude/skills/{s}/skill.py" for s in batch]
    for skill_id in batch:
        manifest_path = root / ".claude" / "skills" / skill_id / "manifest.json"
        if manifest_path.exists():
            paths_to_snap.append(str(manifest_path.relative_to(root)))
    snap_dir = run_root / "pre_run_snapshot"
    create_snapshot(root, paths_to_snap, snap_dir)

    # Convert: run promote_to_native --apply (it finds adapter skills and converts)
    r = subprocess.run(
        [sys.executable, "scripts/promote_to_native.py", "--apply"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        report["failures"].append("promote_to_native failed")
        report["validation_pass"] = False
        restore_snapshot(root, snap_dir)
        report["rollback"] = True
        (run_root / "conversion_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (run_root / "rollback_map.json").write_text(json.dumps({"restored_from": str(snap_dir)}, indent=2) + "\n", encoding="utf-8")
        print("Conversion failed; rollback applied.", file=sys.stderr)
        return 1

    if not run_gates(root):
        report["validation_pass"] = False
        restore_snapshot(root, snap_dir)
        report["rollback"] = True
        (run_root / "conversion_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (run_root / "rollback_map.json").write_text(json.dumps({"restored_from": str(snap_dir)}, indent=2) + "\n", encoding="utf-8")
        print("Gates failed after conversion; rollback applied.", file=sys.stderr)
        return 1

    report["converted"] = batch
    report["validation_pass"] = True
    (run_root / "conversion_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Batch complete:", report["converted"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
