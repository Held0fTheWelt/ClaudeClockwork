"""Phase 54 — Migration system: registry, engine, multiple migrations."""
from pathlib import Path

import pytest

from claudeclockwork.migrations.engine import MigrationRegistry, run_migrations


def test_registry_migrate_v1_to_v2() -> None:
    reg = MigrationRegistry()
    reg.register(1, 2, lambda d: {**d, "schema_version": 2})
    out = reg.migrate({"schema_version": 1, "x": 1}, 1, 2)
    assert out["schema_version"] == 2
    assert out["x"] == 1


def test_run_migrations_dry_run(tmp_path: Path) -> None:
    cfg = tmp_path / "config.json"
    cfg.write_text('{"schema_version": 1}', encoding="utf-8")
    reg = MigrationRegistry()
    reg.register(1, 2, lambda d: {**d, "schema_version": 2})
    result = run_migrations(cfg, reg, target_version=2, dry_run=True)
    assert result["written"] is False
    assert result["final_version"] == 2
    assert cfg.read_text() == '{"schema_version": 1}'


def test_run_migrations_apply(tmp_path: Path) -> None:
    cfg = tmp_path / "config.json"
    cfg.write_text('{"schema_version": 1}', encoding="utf-8")
    reg = MigrationRegistry()
    reg.register(1, 2, lambda d: {**d, "schema_version": 2})
    result = run_migrations(cfg, reg, target_version=2, dry_run=False)
    assert result["written"] is True
    import json
    assert json.loads(cfg.read_text())["schema_version"] == 2
