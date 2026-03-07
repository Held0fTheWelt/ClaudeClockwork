from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.executor.executor import SkillExecutor
from claudeclockwork.core.planner.planner import Planner
from claudeclockwork.core.plugin.dependency import PluginDependencyResolver
from claudeclockwork.core.plugin.loader import PluginLoader
from claudeclockwork.core.plugin.registry import PluginRegistry
from claudeclockwork.core.registry.skill_registry import SkillRegistry
from claudeclockwork.core.security.permissions import PermissionManager


DEFAULT_SKILL_ROOTS = [".claude/skills", "skills"]


def _load_permissions(project_root: Path) -> PermissionManager:
    cfg_path = project_root / ".claude" / "config" / "permissions.json"
    if not cfg_path.exists():
        return PermissionManager()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    return PermissionManager(set(cfg.get("allowed", [])), set(cfg.get("blocked", [])))


def build_plugin_registry(project_root: str | Path) -> PluginRegistry:
    project_root = Path(project_root).resolve()
    manifests = PluginLoader().discover(project_root / "plugins")
    state_path = project_root / "registry" / "plugin_index.json"
    return PluginRegistry(manifests, state_path)


def build_registry(
    project_root: str | Path,
    skills_roots: list[str | Path] | tuple[str | Path, ...] | None = None,
    strict: bool = False,
) -> SkillRegistry:
    registry = SkillRegistry(project_root=project_root, skills_roots=skills_roots or DEFAULT_SKILL_ROOTS, strict=strict)
    registry.rebuild()
    return registry


def build_executor(project_root: str | Path) -> SkillExecutor:
    project_root = Path(project_root).resolve()
    plugin_registry = build_plugin_registry(project_root)
    dependency_resolver = PluginDependencyResolver(plugin_registry)
    return SkillExecutor(
        build_registry(project_root),
        _load_permissions(project_root),
        dependency_resolver=dependency_resolver,
    )


def build_planner(project_root: str | Path) -> Planner:
    return Planner(build_registry(project_root))
