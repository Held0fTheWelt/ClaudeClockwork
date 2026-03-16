from __future__ import annotations

from pathlib import Path

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry


def test_registry_includes_added_skills() -> None:
    project_root = Path(__file__).resolve().parents[1]
    registry = build_registry(project_root)
    names = {item.name for item in registry.list_skills(enabled_only=False)}
    assert 'manifest_validate' in names
    assert 'plugin_scaffold' in names
    assert 'legacy_skill_inventory' in names


def test_manifest_validate_runs_cleanly() -> None:
    project_root = Path(__file__).resolve().parents[1]
    result = run_manifest_skill({"request_id": "test", "skill_id": "manifest_validate", "inputs": {}}, project_root)
    assert result is not None
    assert result["status"] == "ok"
    assert result["outputs"]["valid"] is True


def test_plugin_scaffold_dry_run() -> None:
    project_root = Path(__file__).resolve().parents[1]
    result = run_manifest_skill(
        {
            "request_id": "test",
            "skill_id": "plugin_scaffold",
            "inputs": {
                "plugin_name": "example_plugin",
                "description": "Example plugin scaffold",
                "dry_run": True,
            },
        },
        project_root,
    )
    assert result is not None
    assert result["status"] == "ok"
    assert result["outputs"]["dry_run"] is True
    assert result["outputs"]["plugin_root"] == "plugins/example_plugin"
