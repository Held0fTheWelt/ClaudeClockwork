from __future__ import annotations

from dataclasses import asdict

from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.core.registry.skill_registry import SkillRegistry
from claudeclockwork.core.security.permissions import PermissionManager
from claudeclockwork.core.mode import ModeGuard, ModeViolationError, ModeManager
from claudeclockwork.core.mode.mode_validator import ModeMetadataValidator


class SkillExecutor:
    def __init__(
        self,
        registry: SkillRegistry,
        permission_manager: PermissionManager,
        dependency_resolver=None,
        mode_manager: ModeManager | None = None,
    ) -> None:
        self.registry = registry
        self.permission_manager = permission_manager
        self._dependency_resolver = dependency_resolver
        self.mode_guard = ModeGuard(mode_manager)
        self.mode_validator = ModeMetadataValidator()

    def execute(self, skill_id: str, context: ExecutionContext, **kwargs) -> SkillResult:
        """
        Execute a skill with mode enforcement.

        Hard gates (in order):
        1. Mode state validation (fail closed)
        2. Mode metadata validation (fail closed)
        3. Skill manifest mode compatibility check
        4. Permission validation
        5. Dependency resolution
        6. Skill execution

        Args:
            skill_id: ID of skill to execute
            context: Execution context
            **kwargs: Additional arguments

        Returns:
            SkillResult with execution outcome
        """
        # GATE 1: Validate mode state (fail closed)
        mode_valid, mode_errors = self.mode_validator.validate_mode_state()
        if not mode_valid:
            return SkillResult(
                False,
                skill_id,
                error=f"Mode system error: {'; '.join(mode_errors)}"
            )

        manifest = self.registry.get_manifest(skill_id)
        if manifest is None:
            return SkillResult(False, skill_id, error="Skill not found")

        # GATE 2: Validate manifest has required mode metadata (fail closed)
        manifest_dict = asdict(manifest)
        metadata_valid, metadata_errors = self.mode_validator.validate_skill_manifest(manifest_dict)
        if not metadata_valid:
            return SkillResult(
                False,
                skill_id,
                error=f"Skill mode metadata error: {'; '.join(metadata_errors)}"
            )

        # GATE 3: Check if skill is compatible with active mode
        try:
            mode_requirements = manifest.metadata.get("mode_requirements", {})
            agent_type = mode_requirements.get("agent_type")

            if agent_type == "claude":
                self.mode_guard.check_claude_execution_allowed()
            elif agent_type == "ollama":
                self.mode_guard.check_ollama_execution_allowed()
            elif agent_type == "hybrid":
                self.mode_guard.check_mixed_execution_allowed()

        except ModeViolationError as e:
            return SkillResult(False, skill_id, error=str(e))

        # GATE 4: Permission validation
        ok, error = self.permission_manager.validate(manifest.permissions)
        if not ok:
            return SkillResult(False, skill_id, error=error)

        # GATE 5: Dependency resolution
        if self._dependency_resolver is not None:
            dep_errors = self._dependency_resolver.validate_skill(manifest)
            if dep_errors:
                return SkillResult(False, skill_id, error="; ".join(dep_errors))

        # GATE 6: Execute skill
        skill = self.registry.create(skill_id)
        return skill.run(context, **kwargs)
