from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.core.plugin.loader import PluginLoader
from claudeclockwork.core.plugin.dependency import PluginDependencyResolver
from claudeclockwork.core.models.skill_manifest import SkillManifest
from claudeclockwork.runtime import build_plugin_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_plugin_discovery_finds_both_plugins() -> None:
    """PluginLoader must discover both filesystem and git plugins."""
    plugins = PluginLoader().discover(PROJECT_ROOT / "plugins")
    ids = {p.id for p in plugins}
    assert "filesystem" in ids
    assert "git" in ids
    assert len(plugins) == 2


def test_plugin_manifests_have_required_fields() -> None:
    """Every discovered plugin must have id, name, version, description."""
    plugins = PluginLoader().discover(PROJECT_ROOT / "plugins")
    for p in plugins:
        assert p.id, f"{p.name}: missing id"
        assert p.name, f"{p.id}: missing name"
        assert p.version, f"{p.id}: missing version"
        assert p.description, f"{p.id}: missing description"


def test_plugin_registry_enable_disable_persists(tmp_path) -> None:
    """enable/disable state must survive a registry reload from the same state file."""
    state_path = tmp_path / "plugin_index.json"
    plugins = PluginLoader().discover(PROJECT_ROOT / "plugins")

    registry = build_plugin_registry.__wrapped__(plugins, state_path) if hasattr(build_plugin_registry, "__wrapped__") else None
    # Build directly to use a custom state path
    from claudeclockwork.core.plugin.registry import PluginRegistry
    registry = PluginRegistry(plugins, state_path)

    registry.enable("filesystem")
    assert registry.is_enabled("filesystem")

    registry.disable("filesystem")
    assert not registry.is_enabled("filesystem")

    # Reload from disk — state must persist
    registry2 = PluginRegistry(plugins, state_path)
    assert not registry2.is_enabled("filesystem")
    assert registry2.is_enabled("git")


def test_dependency_resolver_passes_when_no_requires() -> None:
    """Skills without requires_plugins pass unconditionally."""
    plugins = PluginLoader().discover(PROJECT_ROOT / "plugins")
    from claudeclockwork.core.plugin.registry import PluginRegistry
    registry = PluginRegistry(plugins, PROJECT_ROOT / "registry" / "plugin_index.json")
    resolver = PluginDependencyResolver(registry)

    manifest = SkillManifest(
        name="test_skill",
        version="0.1.0",
        category="qa",
        description="A test skill.",
        entrypoint="skills.qa.qa_gate.skill:QaGateSkill",
        metadata={},  # no requires_plugins
    )
    errors = resolver.validate_skill(manifest)
    assert errors == []


def test_dependency_resolver_fails_when_plugin_disabled(tmp_path) -> None:
    """Resolver must return an error when a required plugin is disabled."""
    plugins = PluginLoader().discover(PROJECT_ROOT / "plugins")
    from claudeclockwork.core.plugin.registry import PluginRegistry
    registry = PluginRegistry(plugins, tmp_path / "plugin_index.json")
    registry.disable("filesystem")

    resolver = PluginDependencyResolver(registry)
    manifest = SkillManifest(
        name="fs_skill",
        version="0.1.0",
        category="misc",
        description="Needs filesystem.",
        entrypoint="skills.meta.skill_scaffold.skill:SkillScaffoldSkill",
        metadata={"requires_plugins": ["filesystem"]},
    )
    errors = resolver.validate_skill(manifest)
    assert len(errors) == 1
    assert "filesystem" in errors[0]


def test_plugin_registry_export_reflects_live_state() -> None:
    """plugin_registry_export must return live plugin state."""
    result = run_manifest_skill(
        {"request_id": "test", "skill_id": "plugin_registry_export", "inputs": {}},
        PROJECT_ROOT,
    )
    assert result is not None
    assert result["status"] == "ok"
    assert "plugins" in result["outputs"]
    assert result["outputs"]["plugin_count"] == 2
    plugin_ids = {p["id"] for p in result["outputs"]["plugins"]}
    assert "filesystem" in plugin_ids
    assert "git" in plugin_ids


def test_plugin_healthcheck_no_hook_returns_ok() -> None:
    """CLI healthcheck with no hook declared must return ok."""
    import subprocess, sys
    r = subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli", "--plugin-healthcheck", "filesystem",
         "--project-root", str(PROJECT_ROOT)],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT),
    )
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["status"] == "ok"


def test_skill_fails_cleanly_when_required_plugin_disabled(tmp_path) -> None:
    """Executor must fail with a descriptive error when a skill's plugin dep is disabled."""
    from claudeclockwork.core.executor.executor import SkillExecutor
    from claudeclockwork.core.models.execution_context import ExecutionContext
    from claudeclockwork.core.plugin.registry import PluginRegistry
    from claudeclockwork.core.security.permissions import PermissionManager
    from claudeclockwork.runtime import build_registry

    plugins = PluginLoader().discover(PROJECT_ROOT / "plugins")
    plugin_reg = PluginRegistry(plugins, tmp_path / "plugin_index.json")
    plugin_reg.disable("filesystem")

    skill_registry = build_registry(PROJECT_ROOT)
    resolver = PluginDependencyResolver(plugin_reg)

    # Patch skill_scaffold manifest in memory to require filesystem
    manifest = skill_registry.get_manifest("skill_scaffold")
    assert manifest is not None
    manifest.metadata["requires_plugins"] = ["filesystem"]

    executor = SkillExecutor(skill_registry, PermissionManager(), dependency_resolver=resolver)
    context = ExecutionContext(request_id="test", user_input="skill_scaffold", working_directory=str(PROJECT_ROOT))
    result = executor.execute("skill_scaffold", context, skill_name="x", category="misc", description="test", dry_run=True)

    assert result.success is False
    assert "filesystem" in (result.error or "")

    # Cleanup: remove the patched requires_plugins
    manifest.metadata.pop("requires_plugins", None)
