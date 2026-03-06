from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class PluginRegistryExportSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        plugins_root = repo_root / 'plugins'
        items = []
        for plugin_json in sorted(plugins_root.glob('*/plugin.json')):
            try:
                data = json.loads(plugin_json.read_text(encoding='utf-8'))
            except Exception as exc:
                items.append({'name': plugin_json.parent.name, 'path': str(plugin_json.relative_to(repo_root)), 'error': str(exc)})
                continue
            items.append({
                'name': data.get('name', plugin_json.parent.name),
                'version': data.get('version', '0.1.0'),
                'description': data.get('description', ''),
                'permissions': data.get('permissions', []),
                'capabilities': data.get('capabilities', []),
                'requires_plugins': data.get('requires_plugins', []),
                'path': str(plugin_json.relative_to(repo_root)),
            })
        output_path = Path(kwargs.get('output_path') or (repo_root / 'registry' / 'plugin_index.json')).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {'count': len(items), 'plugins': items}
        output_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        return SkillResult(True, 'plugin_registry_export', data={'output_path': str(output_path), 'plugin_count': len(items)})
