from __future__ import annotations

import json
import re
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.runtime import build_registry


class LegacySkillInventorySkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        legacy_root = repo_root / '.claude' / 'tools' / 'skills'
        registry = build_registry(repo_root)
        manifest_names = {item.name for item in registry.list_skills(enabled_only=False)}
        legacy = []
        for py_path in sorted(legacy_root.glob('*.py')):
            if py_path.name in {'__init__.py', 'skill_runner.py'}:
                continue
            text = py_path.read_text(encoding='utf-8', errors='ignore')
            if not re.search(r'^def\s+run\s*\(', text, flags=re.M):
                continue
            legacy.append({
                'name': py_path.stem,
                'wrapped': py_path.stem in manifest_names,
                'path': str(py_path.relative_to(repo_root)),
            })
        wrapped = [item for item in legacy if item['wrapped']]
        unwrapped = [item for item in legacy if not item['wrapped']]
        payload = {
            'legacy_total': len(legacy),
            'wrapped_total': len(wrapped),
            'unwrapped_total': len(unwrapped),
            'coverage_ratio': round((len(wrapped) / len(legacy)) if legacy else 1.0, 4),
            'wrapped': wrapped,
            'unwrapped': unwrapped,
        }
        output_path = kwargs.get('output_path')
        if output_path:
            out = Path(output_path)
            if not out.is_absolute():
                out = repo_root / out
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, indent=2), encoding='utf-8')
            payload['output_path'] = str(out)
        return SkillResult(True, 'legacy_skill_inventory', data=payload)
