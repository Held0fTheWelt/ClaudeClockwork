from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.runtime import build_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_all_manifest_entrypoints_resolve() -> None:
    """Every manifest entrypoint must import and return a SkillBase subclass."""
    registry = build_registry(PROJECT_ROOT)
    skills = registry.list_skills(enabled_only=False)
    assert len(skills) > 0, "Registry must contain at least one skill"
    for manifest in skills:
        cls = registry._classes.get(manifest.name)
        assert cls is not None, f"{manifest.name}: class not loaded into registry"
        assert isinstance(cls, type), f"{manifest.name}: entrypoint did not return a class"
        assert issubclass(cls, SkillBase), f"{manifest.name}: {cls.__name__} is not a SkillBase subclass"


def test_manifest_validate_catches_bad_entrypoint() -> None:
    """manifest_validate must return valid=false for a broken entrypoint."""
    result = run_manifest_skill(
        {
            "request_id": "test_bad_entrypoint",
            "skill_id": "manifest_validate",
            "inputs": {},
        },
        PROJECT_ROOT,
    )
    # All current manifests should be valid
    assert result is not None
    assert result["status"] == "ok"
    assert result["outputs"]["valid"] is True
    assert result["outputs"]["issue_count"] == 0


def test_registry_strict_mode_exposes_validation_errors() -> None:
    """In strict mode, registry.validation_errors is accessible (empty if all manifests valid)."""
    registry = build_registry(PROJECT_ROOT, strict=True)
    assert hasattr(registry, "validation_errors"), "SkillRegistry must expose validation_errors"
    assert isinstance(registry.validation_errors, list)
    # All current manifests should pass basic validation
    assert registry.validation_errors == [], f"Unexpected validation errors: {registry.validation_errors}"


def test_manifest_ids_match_names() -> None:
    """Every manifest.json must have an 'id' field equal to 'name'."""
    import json

    manifest_files = list((PROJECT_ROOT / ".claude" / "skills").rglob("manifest.json"))
    assert len(manifest_files) >= 34, f"Expected at least 34 manifests, found {len(manifest_files)}"
    for p in manifest_files:
        data = json.loads(p.read_text(encoding="utf-8"))
        assert "id" in data, f"{p}: missing 'id' field"
        assert data["id"] == data["name"], f"{p}: id {data['id']!r} != name {data['name']!r}"
