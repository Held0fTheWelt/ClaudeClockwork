#!/usr/bin/env python3
"""
Phase 63 — Migration script: move runtime outputs from .report/ to .clockwork_runtime/reports/.

This script:
1. Scans .report/ for runtime-generated files (JSON, JSONL, PNG, etc.)
2. Moves them to .clockwork_runtime/reports/ preserving directory structure
3. Deletes empty subdirectories in .report/
4. Keeps only .gitkeep and markdown files in .report/

Usage:
    python3 scripts/migrate_report_to_runtime.py [--dry-run] [--verbose]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def find_project_root() -> Path:
    """Find project root by looking for claudeclockwork package."""
    p = Path(__file__).resolve().parent.parent
    if (p / "claudeclockwork" / "__init__.py").is_file():
        return p
    # Fallback to current directory
    return Path.cwd()


def should_migrate(file_path: Path) -> bool:
    """Determine if a file should be migrated to .clockwork_runtime/."""
    name = file_path.name
    suffix = file_path.suffix.lower()

    # Don't migrate special files
    if name == ".gitkeep" or name == "README.md":
        return False

    # Markdown files matching runtime patterns should be migrated
    # (e.g., budget_budget_run-unknown_report_20260307T113732Z.md)
    if suffix == ".md":
        runtime_md_patterns = [
            "budget_budget_run-unknown_report",
            "model_routing_report",
        ]
        for pattern in runtime_md_patterns:
            if pattern in name:
                return True
        # Don't migrate other markdown files (assumed curated)
        return False

    # Migrate runtime file extensions
    runtime_extensions = {".json", ".jsonl", ".png", ".jpg", ".jpeg", ".gif", ".csv", ".tsv"}
    if suffix in runtime_extensions:
        return True

    # Migrate files matching runtime patterns
    runtime_patterns = [
        "budget_budget_run-unknown",
        "model_routing_outcome",
        "model_routing_report",
        "qa_gate_",
    ]
    for pattern in runtime_patterns:
        if pattern in name:
            return True

    return False


def migrate_files(
    project_root: Path,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict[str, int]:
    """
    Migrate runtime files from .report/ to .clockwork_runtime/reports/.

    Args:
        project_root: Project root directory
        dry_run: If True, simulate migration without moving files
        verbose: If True, print detailed progress

    Returns:
        Dict with statistics: migrated, skipped, errors
    """
    report_dir = project_root / ".report"
    runtime_reports_dir = project_root / ".clockwork_runtime" / "reports"

    stats = {"migrated": 0, "skipped": 0, "errors": 0}

    if not report_dir.is_dir():
        print(f"ERROR: .report/ not found at {report_dir}")
        return stats

    if not runtime_reports_dir.is_dir():
        if dry_run:
            print(f"[DRY-RUN] Would create: {runtime_reports_dir}")
        else:
            runtime_reports_dir.mkdir(parents=True, exist_ok=True)
            if verbose:
                print(f"Created: {runtime_reports_dir}")

    # Collect all files to migrate
    files_to_migrate = []
    for file_path in sorted(report_dir.rglob("*")):
        if not file_path.is_file():
            continue

        if should_migrate(file_path):
            files_to_migrate.append(file_path)

    if verbose:
        print(f"Found {len(files_to_migrate)} runtime files to migrate")

    # Migrate each file
    for src_path in files_to_migrate:
        try:
            rel_path = src_path.relative_to(report_dir)
            dst_path = runtime_reports_dir / rel_path

            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            if dry_run:
                print(f"[DRY-RUN] Move: {rel_path}")
            else:
                shutil.move(str(src_path), str(dst_path))
                if verbose:
                    print(f"Migrated: {rel_path}")
                stats["migrated"] += 1

        except Exception as e:
            print(f"ERROR migrating {src_path}: {e}", file=sys.stderr)
            stats["errors"] += 1

    # Clean up empty directories in .report/
    if not dry_run:
        dirs_to_check = list(report_dir.rglob("*"))
        dirs_to_check.sort(reverse=True)  # Process deepest first

        for dir_path in dirs_to_check:
            if not dir_path.is_dir():
                continue
            if dir_path == report_dir:
                continue

            # Check if directory is empty
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    if verbose:
                        print(f"Removed empty directory: {dir_path.relative_to(report_dir)}")
            except OSError:
                pass

    return stats


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate runtime files from .report/ to .clockwork_runtime/reports/"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate migration without moving files",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed progress",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root directory (auto-detected if not specified)",
    )

    args = parser.parse_args()
    root = args.root or find_project_root()

    print(f"Phase 63 — Report Migration")
    print(f"Project root: {root}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print()

    stats = migrate_files(root, dry_run=args.dry_run, verbose=args.verbose)

    print()
    print("Migration Summary:")
    print(f"  Migrated: {stats['migrated']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")

    if stats["errors"] > 0:
        return 1

    if not args.dry_run:
        print()
        print("✓ Migration complete. Runtime files moved to .clockwork_runtime/reports/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
