#!/usr/bin/env python3
"""skill_scaffold

Scaffold a new manifest-based skill package under `.claude/skills/<category>/<skill_name>/` by default.

This repurposes the original legacy scaffold so new work lands in the Full Skill
System instead of only in `.claude/tools/skills/`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


DEFAULT_ROOT = '.claude/skills'


def _ok(req: dict, outputs: dict, warnings: list[str] | None = None, metrics: dict | None = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "skill_scaffold"),
        "status": "ok",
        "outputs": outputs,
        "errors": [],
        "warnings": warnings or [],
        "metrics": metrics or {},
    }


def _fail(req: dict, errors: list[str], warnings: list[str] | None = None, metrics: dict | None = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "skill_scaffold"),
        "status": "fail",
        "outputs": {},
        "errors": errors,
        "warnings": warnings or [],
        "metrics": metrics or {},
    }


def _find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(25):
        if (cur / '.claude').is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()


def _class_name(skill_name: str) -> str:
    return ''.join(part.title() for part in skill_name.split('_')) + 'Skill'


def run(req: dict) -> dict:
    inputs = req.get('inputs', {})
    repo_root = Path(inputs.get('repo_root') or _find_repo_root(Path.cwd())).resolve()
    category = str(inputs.get('category') or 'custom').strip().lower()
    skill_name = str(inputs.get('skill_name') or '').strip().lower()
    description = str(inputs.get('description') or '').strip()
    dry_run = bool(inputs.get('dry_run', True))
    legacy_bridge = bool(inputs.get('legacy_bridge', False))
    root_rel = str(inputs.get('root') or DEFAULT_ROOT).strip().strip('/')

    if not re.match(r'^[a-z][a-z0-9_]+$', skill_name):
        return _fail(req, ['inputs.skill_name must be snake_case and start with a letter'])
    if not re.match(r'^[a-z][a-z0-9_]+$', category):
        return _fail(req, ['inputs.category must be snake_case and start with a letter'])
    if not description:
        return _fail(req, ['inputs.description is required'])

    base_dir = repo_root / root_rel / category / skill_name
    manifest_path = base_dir / 'manifest.json'
    module_path = base_dir / 'skill.py'
    init_path = base_dir / '__init__.py'
    readme_path = base_dir / 'README.md'

    if any(path.exists() for path in [manifest_path, module_path, init_path, readme_path]):
        return _fail(req, ['collision: target skill package already exists'])

    class_name = _class_name(skill_name)
    manifest = {
        'name': skill_name,
        'version': '0.1.0',
        'category': category,
        'description': description,
        'entrypoint': f'skills.{category}.{skill_name}.skill:{class_name}',
        'permissions': list(inputs.get('permissions', [])),
        'aliases': list(inputs.get('aliases', [])),
        'tags': list(inputs.get('tags', [])),
        'enabled': True,
        'trust_level': 'local',
        'inputs': dict(inputs.get('schema_inputs', {})),
        'outputs': dict(inputs.get('schema_outputs', {})),
        'metadata': {'legacy_bridge': legacy_bridge, 'source_root': root_rel},
    }

    if legacy_bridge:
        skill_body = f"from __future__ import annotations\n\nfrom claudeclockwork.legacy.adapter import LegacySkillAdapter\n\n\nclass {class_name}(LegacySkillAdapter):\n    legacy_skill_id = \"{skill_name}\"\n"
    else:
        skill_body = f"from __future__ import annotations\n\nfrom claudeclockwork.core.base.skill_base import SkillBase\nfrom claudeclockwork.core.models.execution_context import ExecutionContext\nfrom claudeclockwork.core.models.skill_result import SkillResult\n\n\nclass {class_name}(SkillBase):\n    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:\n        return SkillResult(True, \"{skill_name}\", data={{\"inputs\": kwargs, \"note\": \"Implement skill logic here.\"}})\n"

    planned = {
        'base_dir': str(base_dir.relative_to(repo_root)),
        'manifest': str(manifest_path.relative_to(repo_root)),
        'module': str(module_path.relative_to(repo_root)),
        'readme': str(readme_path.relative_to(repo_root)),
        'legacy_bridge': legacy_bridge,
        'root': root_rel,
    }
    if dry_run:
        return _ok(req, {'dry_run': True, 'planned': planned, 'manifest_preview': manifest})

    base_dir.mkdir(parents=True, exist_ok=True)
    init_path.write_text('"""skill package"""\n', encoding='utf-8')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    module_path.write_text(skill_body, encoding='utf-8')
    readme_path.write_text(f"# {skill_name}\n\n{description}\n", encoding='utf-8')

    return _ok(req, {'dry_run': False, 'written': planned})
