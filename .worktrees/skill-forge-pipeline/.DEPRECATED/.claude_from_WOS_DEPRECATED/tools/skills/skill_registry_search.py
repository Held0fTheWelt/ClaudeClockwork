#!/usr/bin/env python3
"""skill_registry_search

Search both the manifest-based registries (`.claude/skills/**/manifest.json`, `skills/**/manifest.json`)
and the legacy `.claude/tools/skills/*.py` inventory.

This repurposes the original registry search skill so migration work can search
across both systems during the transition period.
"""

from __future__ import annotations

import json
from pathlib import Path


MANIFEST_ROOTS = ('.claude/skills', 'skills')


def _ok(req: dict, outputs: dict, warnings: list[str] | None = None, metrics: dict | None = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "skill_registry_search"),
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
        "skill_id": req.get("skill_id", "skill_registry_search"),
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


def _score(query_tokens: set[str], corpus: str) -> int:
    corpus = corpus.lower()
    phrase = ' '.join(sorted(query_tokens))
    score = sum(1 for token in query_tokens if token in corpus)
    return score + (2 if phrase and phrase in corpus else 0)


def run(req: dict) -> dict:
    inputs = req.get('inputs', {})
    repo_root = Path(inputs.get('repo_root') or _find_repo_root(Path.cwd())).resolve()
    query = str(inputs.get('query') or '').strip().lower()
    if not query:
        return _fail(req, ['inputs.query is required'])
    max_results = int(inputs.get('max_results') or 25)
    query_tokens = {token for token in query.replace('_', ' ').split() if token}

    manifest_hits: list[dict] = []
    for root_name in MANIFEST_ROOTS:
        manifest_root = repo_root / root_name
        if not manifest_root.exists():
            continue
        for manifest_path in sorted(manifest_root.rglob('manifest.json')):
            try:
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            except Exception:
                continue
            corpus = ' '.join([
                manifest.get('name', ''),
                manifest.get('description', ''),
                manifest.get('category', ''),
                *manifest.get('aliases', []),
                *manifest.get('tags', []),
            ])
            score = _score(query_tokens, corpus)
            if score <= 0:
                continue
            manifest_hits.append({
                'score': score,
                'name': manifest.get('name', manifest_path.parent.name),
                'category': manifest.get('category', ''),
                'description': manifest.get('description', ''),
                'source': str(manifest_path.relative_to(repo_root)),
                'source_root': root_name,
                'type': 'manifest',
            })

    legacy_hits: list[dict] = []
    for py_path in sorted((repo_root / '.claude' / 'tools' / 'skills').glob('*.py')):
        if py_path.name in {'__init__.py', 'skill_runner.py'}:
            continue
        text = py_path.read_text(encoding='utf-8', errors='ignore')
        first_line = next((line.strip(' #') for line in text.splitlines() if line.strip()), '')
        corpus = f"{py_path.stem} {first_line}"
        score = _score(query_tokens, corpus)
        if score <= 0:
            continue
        legacy_hits.append({
            'score': score,
            'name': py_path.stem,
            'description': first_line,
            'source': str(py_path.relative_to(repo_root)),
            'type': 'legacy',
        })

    manifest_hits.sort(key=lambda item: (-item['score'], item['name']))
    legacy_hits.sort(key=lambda item: (-item['score'], item['name']))

    outputs = {
        'repo_root': str(repo_root),
        'query': query,
        'manifest_hits': manifest_hits[:max_results],
        'legacy_hits': legacy_hits[:max_results],
        'summary': {
            'manifest_matches': len(manifest_hits),
            'legacy_matches': len(legacy_hits),
        },
    }
    return _ok(req, outputs, metrics=outputs['summary'])
