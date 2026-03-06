from __future__ import annotations

import json
import re
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class PluginScaffoldSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        plugin_name = str(kwargs.get('plugin_name') or '').strip().lower()
        description = str(kwargs.get('description') or '').strip()
        dry_run = bool(kwargs.get('dry_run', True))
        if not re.match(r'^[a-z][a-z0-9_]+$', plugin_name):
            return SkillResult(False, 'plugin_scaffold', error='plugin_name must be snake_case and start with a letter')
        if not description:
            return SkillResult(False, 'plugin_scaffold', error='description is required')

        base_dir = repo_root / 'plugins' / plugin_name
        plugin_json = base_dir / 'plugin.json'
        readme = base_dir / 'README.md'
        manifest = {
            'name': plugin_name,
            'version': '0.1.0',
            'display_name': plugin_name.replace('_', ' ').title(),
            'description': description,
            'enabled_by_default': True,
            'trust_level': 'local',
            'skills_root': 'skills',
            'requires_plugins': list(kwargs.get('requires_plugins', [])),
            'optional_plugins': list(kwargs.get('optional_plugins', [])),
            'permissions': list(kwargs.get('permissions', [])),
            'capabilities': list(kwargs.get('capabilities', [])),
            'compatibility': {'core_min': '0.1.0', 'core_max': '0.9.999'},
        }
        payload = {
            'plugin_root': str(base_dir.relative_to(repo_root)),
            'plugin_json': str(plugin_json.relative_to(repo_root)),
            'readme': str(readme.relative_to(repo_root)),
            'manifest_preview': manifest,
        }
        if dry_run:
            return SkillResult(True, 'plugin_scaffold', data={'dry_run': True, **payload})

        base_dir.mkdir(parents=True, exist_ok=True)
        (base_dir / 'skills').mkdir(exist_ok=True)
        plugin_json.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        readme.write_text(f'# {plugin_name}\n\n{description}\n', encoding='utf-8')
        return SkillResult(True, 'plugin_scaffold', data={'dry_run': False, **payload})
