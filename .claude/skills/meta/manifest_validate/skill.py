from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.runtime import build_registry


class ManifestValidateSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        registry = build_registry(repo_root)
        issues = []
        checked = 0
        for manifest in registry.list_skills(enabled_only=False):
            checked += 1
            required = {
                'name': manifest.name,
                'category': manifest.category,
                'description': manifest.description,
                'entrypoint': manifest.entrypoint,
            }
            for field_name, value in required.items():
                if not value:
                    issues.append({'skill': manifest.name, 'issue': f'missing:{field_name}'})
            try:
                registry.create(manifest.name)
            except Exception as exc:
                issues.append({'skill': manifest.name, 'issue': f'import_failed:{exc}'})
        payload = {
            'checked': checked,
            'issue_count': len(issues),
            'valid': not issues,
            'issues': issues,
        }
        output_path = kwargs.get('output_path')
        if output_path:
            out = Path(output_path)
            if not out.is_absolute():
                out = repo_root / out
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, indent=2), encoding='utf-8')
            payload['output_path'] = str(out)
        return SkillResult(True, 'manifest_validate', data=payload, warnings=[] if not issues else ['Manifest issues detected'])
