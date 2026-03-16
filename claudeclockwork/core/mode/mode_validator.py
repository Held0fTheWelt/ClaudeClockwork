"""Mode metadata validator: Ensure mode consistency and fail closed."""
from __future__ import annotations

from typing import Any

from .mode_manager import ModeManager


class ModeMetadataValidator:
    """Validates mode metadata and fails closed on unknown/incomplete data."""

    REQUIRED_MODE_FIELDS = {
        "allow_claude",
        "allow_ollama",
        "allow_mixed",
        "require_ollama_available",
    }

    def __init__(self):
        """Initialize validator."""
        self.manager = ModeManager()

    def validate_mode_state(self) -> tuple[bool, list[str]]:
        """
        Validate that mode state is consistent and complete.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        try:
            active_mode = self.manager.get_active_mode()
            if not active_mode:
                errors.append("No active mode set")
                return False, errors

            # Validate mode exists and has required fields
            config = self.manager.get_mode_config(active_mode)
            missing = self.REQUIRED_MODE_FIELDS - set(config.keys())
            if missing:
                errors.append(
                    f"Mode '{active_mode}' missing required fields: {missing}"
                )

            # Validate boolean fields
            for field in ["allow_claude", "allow_ollama", "allow_mixed", "require_ollama_available"]:
                if field in config and not isinstance(config[field], bool):
                    errors.append(
                        f"Field '{field}' must be boolean, got {type(config[field])}"
                    )

            # Validate mode-specific constraints
            if active_mode == "default":
                if config.get("allow_claude"):
                    errors.append("default mode must forbid Claude execution")
                if config.get("allow_mixed"):
                    errors.append("default mode must forbid mixed execution")
                if not config.get("allow_ollama"):
                    errors.append("default mode must allow Ollama execution")

            elif active_mode == "claude-min":
                if config.get("allow_ollama"):
                    errors.append("claude-min mode must forbid Ollama execution")
                if config.get("allow_mixed"):
                    errors.append("claude-min mode must forbid mixed execution")
                if not config.get("allow_claude"):
                    errors.append("claude-min mode must allow Claude execution")

            elif active_mode == "adaptive":
                if not config.get("allow_claude"):
                    errors.append("adaptive mode must allow Claude execution")
                if not config.get("allow_ollama"):
                    errors.append("adaptive mode must allow Ollama execution")
                if not config.get("allow_mixed"):
                    errors.append("adaptive mode must allow mixed execution")

        except Exception as e:
            errors.append(f"Error validating mode state: {str(e)}")

        return len(errors) == 0, errors

    def validate_skill_manifest(self, manifest: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate skill manifest has required mode metadata.

        Args:
            manifest: Skill manifest dict

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check for mode_requirements in metadata
        metadata = manifest.get("metadata", {})
        mode_requirements = metadata.get("mode_requirements", None)

        if mode_requirements is None:
            # FAIL CLOSED: Unknown metadata defaults to most restrictive
            errors.append(
                f"Skill {manifest.get('id')} missing mode_requirements. "
                "Unknown skills default to requiring explicit mode declaration."
            )
            return False, errors

        # Validate mode_requirements structure
        if not isinstance(mode_requirements, dict):
            errors.append(
                f"mode_requirements must be dict, got {type(mode_requirements)}"
            )
            return False, errors

        # Validate mode restrictions
        active_mode = self.manager.get_active_mode()
        mode_config = self.manager.get_mode_config()

        skill_modes = mode_requirements.get("requires_mode", [])
        if skill_modes and active_mode not in skill_modes:
            errors.append(
                f"Skill {manifest.get('id')} requires mode {skill_modes}, "
                f"but active mode is {active_mode}"
            )

        # Validate agent type declaration
        agent_type = mode_requirements.get("agent_type", None)
        if not agent_type:
            errors.append(f"Skill {manifest.get('id')} missing agent_type")
        elif agent_type not in ["ollama", "claude", "hybrid"]:
            errors.append(
                f"Skill {manifest.get('id')} has invalid agent_type: {agent_type}"
            )
        else:
            # Check compatibility with active mode
            if agent_type == "claude" and not mode_config.get("allow_claude"):
                errors.append(
                    f"Skill {manifest.get('id')} requires Claude but active mode forbids it"
                )
            elif agent_type == "ollama" and not mode_config.get("allow_ollama"):
                errors.append(
                    f"Skill {manifest.get('id')} requires Ollama but active mode forbids it"
                )
            elif agent_type == "hybrid" and not mode_config.get("allow_mixed"):
                errors.append(
                    f"Skill {manifest.get('id')} requires mixed execution but active mode forbids it"
                )

        return len(errors) == 0, errors

    def validate_all_manifests(self, manifests: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Validate all skill manifests for mode compliance.

        Args:
            manifests: List of skill manifest dicts

        Returns:
            Validation report dict
        """
        report = {
            "total": len(manifests),
            "valid": 0,
            "invalid": 0,
            "missing_metadata": 0,
            "mode_incompatible": 0,
            "errors": {}
        }

        for manifest in manifests:
            skill_id = manifest.get("id", "unknown")
            is_valid, errors = self.validate_skill_manifest(manifest)

            if is_valid:
                report["valid"] += 1
            else:
                report["invalid"] += 1
                report["errors"][skill_id] = errors

                # Categorize errors
                error_str = " ".join(errors)
                if "missing mode_requirements" in error_str:
                    report["missing_metadata"] += 1
                if "active mode" in error_str:
                    report["mode_incompatible"] += 1

        return report
