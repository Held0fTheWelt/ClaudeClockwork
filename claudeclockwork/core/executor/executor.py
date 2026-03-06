from __future__ import annotations

from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.core.registry.skill_registry import SkillRegistry
from claudeclockwork.core.security.permissions import PermissionManager


class SkillExecutor:
    def __init__(self, registry: SkillRegistry, permission_manager: PermissionManager) -> None:
        self.registry = registry
        self.permission_manager = permission_manager

    def execute(self, skill_id: str, context: ExecutionContext, **kwargs) -> SkillResult:
        manifest = self.registry.get_manifest(skill_id)
        if manifest is None:
            return SkillResult(False, skill_id, error="Skill not found")
        ok, error = self.permission_manager.validate(manifest.permissions)
        if not ok:
            return SkillResult(False, skill_id, error=error)
        skill = self.registry.create(skill_id)
        return skill.run(context, **kwargs)
