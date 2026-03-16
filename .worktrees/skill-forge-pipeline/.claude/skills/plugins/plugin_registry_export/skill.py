from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.runtime import build_plugin_registry


class PluginRegistryExportSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        plugin_registry = build_plugin_registry(repo_root)

        all_plugins = plugin_registry.list_plugins(enabled_only=False)
        items = [
            {
                "id": m.id,
                "name": m.name,
                "version": m.version,
                "description": m.description,
                "permissions": m.permissions,
                "capabilities": m.capabilities,
                "requires_plugins": m.requires_plugins,
                "enabled": plugin_registry.is_enabled(m.id),
                "path": f"plugins/{m.id}/plugin.json",
            }
            for m in all_plugins
        ]

        output_path = Path(
            kwargs.get("output_path") or (repo_root / "registry" / "plugin_index.json")
        ).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"count": len(items), "plugins": items}
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return SkillResult(
            True,
            "plugin_registry_export",
            data={
                "output_path": str(output_path),
                "plugin_count": len(items),
                "plugins": items,
            },
        )
