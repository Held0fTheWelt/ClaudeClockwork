#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


MANIFEST_ROOTS = ('.claude/skills', 'skills')


def _first_nonempty_line(p: Path) -> str:
    try:
        for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
            s = line.strip(' #')
            if s:
                return s[:200]
    except Exception:
        return ''
    return ''


def run(req: dict) -> dict:
    inputs = req.get('inputs', {})
    project_root = Path(inputs.get('project_root', '.')).resolve()
    out_path = Path(inputs.get('out', 'validation_runs/capability_map.json')).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    claude_root = project_root / '.claude'
    skills_dir = claude_root / 'tools' / 'skills'
    agents_dir = claude_root / 'agents'

    manifest_skills = []
    reference_skill_docs = []
    for root_name in MANIFEST_ROOTS:
        manifest_root = project_root / root_name
        if not manifest_root.exists():
            continue
        for p in sorted(manifest_root.rglob('manifest.json')):
            try:
                manifest = json.loads(p.read_text(encoding='utf-8'))
            except Exception:
                continue
            manifest_skills.append({
                'skill_id': manifest.get('name', p.parent.name),
                'category': manifest.get('category', ''),
                'description': manifest.get('description', ''),
                'path': str(p.relative_to(project_root)),
                'entrypoint': manifest.get('entrypoint', ''),
                'system': 'manifest',
                'source_root': root_name,
                'legacy_bridge': bool((manifest.get('metadata') or {}).get('legacy_bridge')),
            })
        for p in sorted(manifest_root.rglob('SKILL.md')):
            reference_skill_docs.append({
                'skill_id': p.parent.name,
                'path': str(p.relative_to(project_root)),
                'system': 'reference_doc',
                'source_root': root_name,
            })

    legacy_skills = []
    for p in sorted(skills_dir.glob('*.py')):
        if p.name in {'__init__.py', 'skill_runner.py'}:
            continue
        txt = p.read_text(encoding='utf-8', errors='ignore')
        if not re.search(r'^def\s+run\s*\(', txt, flags=re.M):
            continue
        legacy_skills.append({
            'skill_id': p.stem,
            'path': str(p.relative_to(project_root)),
            'hint': _first_nonempty_line(p),
            'system': 'legacy',
        })

    agents = [{'agent': p.stem, 'path': str(p.relative_to(project_root))} for p in sorted(agents_dir.rglob('*.md'))]
    schemas = [str(p.relative_to(project_root)) for p in sorted((claude_root / 'contracts' / 'schemas').glob('*.json'))]
    examples = [str(p.relative_to(project_root)) for p in sorted((claude_root / 'contracts' / 'examples').rglob('*.json'))]
    governance = [str(p.relative_to(project_root)) for p in sorted((claude_root / 'governance').glob('*.md'))]

    manifest = {
        'type': 'capability_map',
        'project_root': str(project_root),
        'skills': {
            'manifest': manifest_skills,
            'legacy': legacy_skills,
            'reference_docs': reference_skill_docs,
        },
        'agents': agents,
        'contracts': {'schemas': schemas, 'examples': examples},
        'governance': governance,
    }
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')

    return {
        'type': 'skill_result_spec',
        'request_id': req.get('request_id', ''),
        'skill_id': req.get('skill_id', 'capability_map_build'),
        'status': 'ok',
        'outputs': {
            'out': str(out_path),
            'manifest_skills': len(manifest_skills),
            'legacy_skills': len(legacy_skills),
            'reference_skill_docs': len(reference_skill_docs),
            'agents': len(agents),
        },
        'metrics': {
            'manifest_skills': len(manifest_skills),
            'legacy_skills': len(legacy_skills),
            'reference_skill_docs': len(reference_skill_docs),
            'schemas': len(schemas),
            'examples': len(examples),
            'agents': len(agents),
        },
        'errors': [],
        'warnings': [],
    }
