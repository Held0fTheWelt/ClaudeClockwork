from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class ReferenceSkillCatalogSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        skills_root = repo_root / '.claude' / 'skills'
        items = []
        for path in sorted(skills_root.rglob('*')):
            if not path.is_dir():
                continue
            if path.name.startswith('__'):
                continue
            rel = path.relative_to(skills_root)
            if len(rel.parts) > 2:
                continue
            has_skill_doc = (path / 'SKILL.md').exists()
            has_manifest = (path / 'manifest.json').exists()
            has_readme = (path / 'README.md').exists()
            if not (has_skill_doc or has_manifest or has_readme):
                continue
            items.append({
                'name': path.name,
                'path': str(path.relative_to(repo_root)),
                'has_skill_doc': has_skill_doc,
                'has_manifest': has_manifest,
                'has_readme': has_readme,
                'category_hint': rel.parts[0] if len(rel.parts) > 1 else 'reference',
            })
        summary = {
            'total_items': len(items),
            'skill_docs': sum(1 for item in items if item['has_skill_doc']),
            'manifests': sum(1 for item in items if item['has_manifest']),
            'readmes': sum(1 for item in items if item['has_readme']),
        }
        payload = {'summary': summary, 'items': items}
        output_path = kwargs.get('output_path')
        if output_path:
            out = Path(output_path)
            if not out.is_absolute():
                out = repo_root / out
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, indent=2), encoding='utf-8')
            payload['output_path'] = str(out)
        return SkillResult(True, 'reference_skill_catalog', data=payload)
