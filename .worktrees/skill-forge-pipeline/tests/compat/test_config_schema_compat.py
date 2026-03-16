"""
Phase 44 — Compatibility tests for config schema migration.

Validates that migration from at least one old schema version is deterministic
and CI-safe. Minimal migration path for tests; full migration system is Phase 54.
"""
from __future__ import annotations

import json
from pathlib import Path

# Minimal compat: "old" config has config_version 1, "migrated" has 2 with required keys
CONFIG_SCHEMA_V1 = {"config_version": 1, "legacy_key": "value"}
CONFIG_SCHEMA_V2 = {"config_version": 2, "legacy_key": "value", "migrated": True}


def _migrate_v1_to_v2(data: dict) -> dict:
    """Deterministic migration from schema version 1 to 2 (compat test only)."""
    if data.get("config_version") != 1:
        return data
    out = dict(data)
    out["config_version"] = 2
    out["migrated"] = True
    return out


def test_config_migration_v1_to_v2_deterministic() -> None:
    """Migrating v1 config produces v2 structure with required keys."""
    migrated = _migrate_v1_to_v2(CONFIG_SCHEMA_V1)
    assert migrated["config_version"] == 2
    assert migrated.get("migrated") is True
    assert migrated.get("legacy_key") == "value"


def test_config_migration_idempotent_on_v2() -> None:
    """Already-v2 config is unchanged by migration."""
    migrated = _migrate_v1_to_v2(CONFIG_SCHEMA_V2)
    assert migrated["config_version"] == 2
    assert migrated == CONFIG_SCHEMA_V2
