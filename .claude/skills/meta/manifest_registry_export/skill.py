from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.runtime import build_registry


class ManifestRegistryExportSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        output_path = Path(kwargs.get("output_path") or (repo_root / "registry" / "skill_index.json")).resolve()
        registry = build_registry(repo_root)
        items = []
        for manifest in registry.list_skills(enabled_only=False):
            items.append({
                "name": manifest.name,
                "category": manifest.category,
                "version": manifest.version,
                "entrypoint": manifest.entrypoint,
                "enabled": manifest.enabled,
                "aliases": manifest.aliases,
                "tags": manifest.tags,
                "legacy_bridge": bool(manifest.metadata.get("legacy_bridge")),
                "manifest_path": manifest.metadata.get("manifest_path", ""),
                "source_root": manifest.metadata.get("source_root", ""),
            })
        payload = {"count": len(items), "skills": items}
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return SkillResult(True, "manifest_registry_export", data={"output_path": str(output_path), "skill_count": len(items)})
