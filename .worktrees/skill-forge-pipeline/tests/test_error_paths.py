from __future__ import annotations

import pytest
from pathlib import Path

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.registry.loader import SkillLoader
from claudeclockwork.runtime import build_executor, build_registry

ROOT = Path(__file__).resolve().parents[1]


def test_bridge_returns_none_for_unknown_skill() -> None:
    result = run_manifest_skill({"request_id": "x", "skill_id": "no_such_skill", "inputs": {}}, ROOT)
    assert result is None


def test_registry_get_manifest_unknown() -> None:
    registry = build_registry(ROOT)
    assert registry.get_manifest("definitely_not_a_skill") is None


def test_registry_create_unknown_raises() -> None:
    registry = build_registry(ROOT)
    with pytest.raises(KeyError):
        registry.create("no_such_skill")


def test_executor_unknown_skill_returns_fail() -> None:
    executor = build_executor(ROOT)
    context = ExecutionContext(request_id="t", user_input="x", working_directory=str(ROOT))
    result = executor.execute("unknown_skill_xyz", context)
    assert result.success is False


def test_loader_bad_module_raises() -> None:
    with pytest.raises((ModuleNotFoundError, ImportError)):
        SkillLoader.load_skill_class("nonexistent.module.path:SomeClass")


def test_loader_bad_class_raises() -> None:
    with pytest.raises(AttributeError):
        SkillLoader.load_skill_class("claudeclockwork.runtime:NonExistentClass")


def test_bridge_empty_skill_id() -> None:
    result = run_manifest_skill({"request_id": "x", "skill_id": "", "inputs": {}}, ROOT)
    assert result is None
