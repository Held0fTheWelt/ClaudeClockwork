"""
Phase 17 — Adapter elimination tests.

Verifies LegacySkillAdapter is removed and all manifest skills are native.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.runtime import build_registry

ROOT = Path(__file__).resolve().parents[1]


def test_no_legacy_adapter_import() -> None:
    """LegacySkillAdapter must not be importable (adapter removed in Phase 17)."""
    with pytest.raises(ImportError):
        from claudeclockwork.legacy.adapter import LegacySkillAdapter  # noqa: F401


def test_all_manifests_have_legacy_bridge_false() -> None:
    """Every .claude/skills/**/manifest.json must have metadata.legacy_bridge === false."""
    skills_root = ROOT / ".claude" / "skills"
    if not skills_root.is_dir():
        pytest.skip("No .claude/skills")
    violations: list[str] = []
    for manifest_path in skills_root.rglob("manifest.json"):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        meta = data.get("metadata") or {}
        lb = meta.get("legacy_bridge")
        # Phase 17: legacy_bridge must be exactly false (boolean)
        if lb is not False:
            violations.append(f"{manifest_path.relative_to(ROOT)}: legacy_bridge={lb!r}")
    assert not violations, "Manifests with legacy_bridge != false:\n" + "\n".join(violations)


def test_all_skills_are_native_skillbase() -> None:
    """Every loaded skill class must be a subclass of SkillBase (no LegacySkillAdapter in MRO)."""
    from claudeclockwork.core.base.skill_base import SkillBase

    registry = build_registry(ROOT)
    not_native: list[str] = []
    for manifest in registry.list_skills(enabled_only=False):
        cls = registry._classes.get(manifest.name)
        if cls is None:
            continue
        if not issubclass(cls, SkillBase):
            not_native.append(manifest.name)
        mro_names = [c.__name__ for c in cls.__mro__]
        if "LegacySkillAdapter" in mro_names:
            not_native.append(f"{manifest.name} (LegacySkillAdapter in MRO)")
    assert not not_native, "Skills not native SkillBase: " + ", ".join(not_native)
