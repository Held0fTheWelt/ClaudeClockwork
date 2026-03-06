from __future__ import annotations

from claudeclockwork.core.models.skill_manifest import SkillManifest
from claudeclockwork.core.plugin.registry import PluginRegistry


class PluginDependencyResolver:
    """Validates that a skill's declared plugin dependencies are satisfied."""

    def __init__(self, plugin_registry: PluginRegistry) -> None:
        self._registry = plugin_registry

    def validate_skill(self, manifest: SkillManifest) -> list[str]:
        """
        Return a list of dependency error strings.
        Empty list means all dependencies are satisfied.

        Reads optional `requires_plugins` list from skill manifest metadata.
        Skills without this field pass unconditionally.
        """
        required: list[str] = manifest.metadata.get("requires_plugins", [])
        if not required:
            return []

        errors: list[str] = []
        for plugin_id in required:
            if not self._registry.is_enabled(plugin_id):
                errors.append(
                    f"required plugin {plugin_id!r} is not enabled — "
                    f"enable it via: plugin_registry.enable('{plugin_id}')"
                )
        return errors
