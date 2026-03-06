#!/usr/bin/env python3
"""
Seed / refresh baseline snapshots for the Phase 6 diff gates.

Run this after adding skills or plugins, then commit the updated baselines:
    python3 scripts/update_baselines.py
    git add .llama_runtime/eval/baselines/
    git commit -m "chore: update gate baselines"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / ".claude"))

BASELINES_DIR = ROOT / ".llama_runtime" / "eval" / "baselines"
BASELINES_DIR.mkdir(parents=True, exist_ok=True)

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry, build_plugin_registry


def update_capability_map_baseline() -> None:
    registry = build_registry(ROOT)
    manifests = registry.list_skills(enabled_only=False)
    skill_ids = sorted(m.name for m in manifests)

    result = run_manifest_skill(
        {"request_id": "baseline", "skill_id": "capability_map_build", "inputs": {}},
        ROOT,
    )
    if result is None or result.get("status") != "ok":
        print(f"ERROR: capability_map_build failed: {result}", file=sys.stderr)
        sys.exit(1)

    baseline = {
        "manifest_skills": result["outputs"]["manifest_skills"],
        "legacy_skills": result["outputs"].get("legacy_skills", 0),
        "skill_ids": skill_ids,
    }
    path = BASELINES_DIR / "capability_map.json"
    path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"Updated capability_map baseline: {len(skill_ids)} skills → {path}")


def update_plugin_index_baseline() -> None:
    plugin_reg = build_plugin_registry(ROOT)
    all_plugins = plugin_reg.list_plugins(enabled_only=False)
    plugin_ids = sorted(p.id for p in all_plugins)

    result = run_manifest_skill(
        {"request_id": "baseline", "skill_id": "plugin_registry_export", "inputs": {}},
        ROOT,
    )
    if result is None or result.get("status") != "ok":
        print(f"ERROR: plugin_registry_export failed: {result}", file=sys.stderr)
        sys.exit(1)

    baseline = {
        "plugin_count": result["outputs"]["plugin_count"],
        "plugin_ids": plugin_ids,
    }
    path = BASELINES_DIR / "plugin_index.json"
    path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"Updated plugin_index baseline: {len(plugin_ids)} plugins → {path}")


if __name__ == "__main__":
    print("Seeding Phase 6 gate baselines...")
    update_capability_map_baseline()
    update_plugin_index_baseline()
    print("Done. Commit .llama_runtime/eval/baselines/ to lock the baseline.")
