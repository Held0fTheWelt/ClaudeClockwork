#!/usr/bin/env python3
"""
Phase 27 — Batch planner for adapter elimination. Produces deterministic batch list.

Usage:
  python scripts/adapter_batch_plan.py [--batch-size N] [--output path]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def find_adapter_skill_ids(root: Path) -> list[str]:
    """Skill ids that still use LegacySkillAdapter (Phase 17 leaves 0 in normal repo)."""
    skills_root = root / ".claude" / "skills"
    if not skills_root.is_dir():
        return []
    ids_: list[str] = []
    for skill_dir in sorted(skills_root.rglob("skill.py")):
        try:
            text = skill_dir.read_text(encoding="utf-8")
        except OSError:
            continue
        if "LegacySkillAdapter" in text:
            ids_.append(skill_dir.parent.name)
    return ids_


def plan_batch(root: Path, batch_size: int) -> list[str]:
    """Deterministic batch: low-risk first (alphabetical), capped at batch_size."""
    candidates = find_adapter_skill_ids(root)
    # Stable sort; same repo state => same list
    return sorted(candidates)[:batch_size]


def main() -> int:
    ap = argparse.ArgumentParser(description="Adapter batch planner (Phase 27).")
    ap.add_argument("--batch-size", type=int, default=50, help="Max skills per batch")
    ap.add_argument("--output", type=str, default="", help="Write JSON list to file")
    args = ap.parse_args()
    root = Path.cwd()
    if not (root / ".claude" / "skills").is_dir():
        print("Run from repo root.", file=sys.stderr)
        return 1
    batch = plan_batch(root, args.batch_size)
    if args.output:
        Path(args.output).write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(batch))
    return 0


if __name__ == "__main__":
    sys.exit(main())
