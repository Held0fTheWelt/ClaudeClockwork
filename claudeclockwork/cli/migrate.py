"""Phase 54 — migrate CLI: dry-run and apply."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from claudeclockwork.migrations.engine import MigrationRegistry, run_migrations


def _default_registry() -> MigrationRegistry:
    r = MigrationRegistry()
    r.register(1, 2, lambda d: {**d, "schema_version": 2, "migrated_v1": True})
    return r


def main() -> int:
    parser = argparse.ArgumentParser(description="Config/schema migration")
    parser.add_argument("--config", default=".clockwork_runtime/config.json", help="Config file path")
    parser.add_argument("--dry-run", action="store_true", help="Do not write")
    parser.add_argument("--apply", action="store_true", help="Write migrated config")
    parser.add_argument("--project-root", default=".", type=str)
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    config_path = root / args.config
    dry_run = not args.apply
    result = run_migrations(config_path, _default_registry(), target_version=2, dry_run=dry_run)
    print(json.dumps(result, indent=2))
    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
