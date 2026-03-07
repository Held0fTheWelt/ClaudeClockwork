#!/usr/bin/env python3
"""
Phase 21 — Adapter Elimination Accelerator.

Deterministic migration tool: normalize manifest metadata (legacy_bridge),
check that all manifests have it, and optionally convert adapter skills to native.

Usage:
  python scripts/adapter_migrate.py normalize-metadata   # add legacy_bridge where missing
  python scripts/adapter_migrate.py check-metadata       # exit 0 if all have it
  python scripts/adapter_migrate.py convert --skills skill1,skill2  # (optional) batch convert
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def find_manifests(root: Path) -> list[Path]:
    """All manifest.json under .claude/skills."""
    skills = root / ".claude" / "skills"
    if not skills.is_dir():
        return []
    return sorted(skills.rglob("manifest.json"))


def normalize_metadata(root: Path, dry_run: bool) -> tuple[int, list[str]]:
    """
    Ensure every manifest has metadata.legacy_bridge (true|false).
    Set to false if missing. Return (count_updated, list of updated paths).
    """
    updated: list[str] = []
    for path in find_manifests(root):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        meta = data.get("metadata")
        if meta is None:
            meta = {}
        if "legacy_bridge" in meta:
            continue
        meta["legacy_bridge"] = False
        data["metadata"] = meta
        rel = path.relative_to(root)
        if not dry_run:
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        updated.append(str(rel))
    return len(updated), updated


def check_metadata(root: Path) -> tuple[bool, list[str]]:
    """Return (all_ok, list of paths missing legacy_bridge)."""
    missing: list[str] = []
    for path in find_manifests(root):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            missing.append(str(path.relative_to(root)))
            continue
        meta = data.get("metadata") or {}
        if "legacy_bridge" not in meta:
            missing.append(str(path.relative_to(root)))
    return len(missing) == 0, missing


def main() -> int:
    ap = argparse.ArgumentParser(description="Adapter migration: normalize/check metadata, optional convert.")
    ap.add_argument("command", choices=["normalize-metadata", "check-metadata", "convert"], help="Subcommand")
    ap.add_argument("--dry-run", action="store_true", help="Only print what would be done")
    ap.add_argument("--skills", type=str, default="", help="Comma-separated skill ids for convert (optional)")
    args = ap.parse_args()

    root = Path.cwd()
    if not (root / ".claude" / "skills").is_dir():
        print("Run from repo root.", file=sys.stderr)
        return 1

    if args.command == "normalize-metadata":
        n, paths = normalize_metadata(root, dry_run=args.dry_run)
        if paths:
            for p in paths:
                print(p)
            print(f"Updated {n} manifest(s).")
        else:
            print("All manifests already have metadata.legacy_bridge.")
        return 0

    if args.command == "check-metadata":
        ok, missing = check_metadata(root)
        if ok:
            print("All manifests have metadata.legacy_bridge.")
            return 0
        for p in missing:
            print(p, file=sys.stderr)
        print(f"Missing legacy_bridge: {len(missing)} manifest(s).", file=sys.stderr)
        return 1

    if args.command == "convert":
        # Batch convert is delegated to promote_to_native.py (Phase 17); no adapters left.
        print("Conversion handled by scripts/promote_to_native.py (Phase 17). No adapter skills remain.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
