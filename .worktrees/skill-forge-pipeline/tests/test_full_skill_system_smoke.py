from __future__ import annotations

from pathlib import Path

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry


def test_registry_discovers_manifest_skills() -> None:
    project_root = Path(__file__).resolve().parents[1]
    registry = build_registry(project_root)
    names = {item.name for item in registry.list_skills(enabled_only=False)}
    assert "skill_registry_search" in names
    assert "capability_map_build" in names


def test_legacy_bridge_executes_wrapped_skill() -> None:
    project_root = Path(__file__).resolve().parents[1]
    result = run_manifest_skill({"request_id": "test", "skill_id": "capability_map_build", "inputs": {}}, project_root)
    assert result is not None
    assert result["status"] == "ok"
