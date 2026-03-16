#!/usr/bin/env python3
"""
sync_version.py — Phase 72: Version SSOT sync utility.

Reads the canonical version from .claude/VERSION and writes it to root VERSION,
ensuring both files are in sync. Running twice is idempotent.

Usage:
    python3 scripts/sync_version.py [--dry-run] [--repo-root PATH]

Exit codes:
    0: synced (or already in sync)
    1: error (canonical version missing or unreadable)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def sync_version(repo_root: Path, dry_run: bool = False) -> dict:
    """
    Sync root VERSION from .claude/VERSION (SSOT).

    Returns:
        {"status": "ok"|"dry_run"|"already_synced"|"error",
         "canonical": str, "root": str|None, "message": str}
    """
    canonical_path = repo_root / ".claude" / "VERSION"
    root_path = repo_root / "VERSION"

    if not canonical_path.is_file():
        return {
            "status": "error",
            "canonical": None,
            "root": None,
            "message": f"Canonical version file not found: {canonical_path}",
        }

    try:
        canonical = canonical_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return {
            "status": "error",
            "canonical": None,
            "root": None,
            "message": f"Cannot read {canonical_path}: {exc}",
        }

    root_val: str | None = None
    if root_path.is_file():
        try:
            root_val = root_path.read_text(encoding="utf-8").strip()
        except OSError:
            root_val = None

    if root_val == canonical:
        return {
            "status": "already_synced",
            "canonical": canonical,
            "root": root_val,
            "message": f"VERSION already matches .claude/VERSION ({canonical})",
        }

    if dry_run:
        return {
            "status": "dry_run",
            "canonical": canonical,
            "root": root_val,
            "message": f"Would write {canonical!r} -> VERSION (dry_run; was {root_val!r})",
        }

    try:
        root_path.write_text(canonical + "\n", encoding="utf-8")
    except OSError as exc:
        return {
            "status": "error",
            "canonical": canonical,
            "root": root_val,
            "message": f"Cannot write {root_path}: {exc}",
        }

    return {
        "status": "ok",
        "canonical": canonical,
        "root": canonical,
        "message": f"Synced VERSION={canonical} (was {root_val!r})",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync root VERSION from .claude/VERSION SSOT")
    parser.add_argument("--dry-run", action="store_true", help="Report only, do not write")
    parser.add_argument("--repo-root", default=".", help="Path to repo root (default: .)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    result = sync_version(repo_root, dry_run=args.dry_run)

    print(result["message"])
    return 0 if result["status"] in ("ok", "already_synced", "dry_run") else 1


if __name__ == "__main__":
    raise SystemExit(main())
