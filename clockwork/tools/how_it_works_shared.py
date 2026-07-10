from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from clockwork.tools.uml_shared import RepoScan, sanitize_alias, write_json, write_text

MAX_GUIDE_RELATIONS = 8
MAX_GUIDE_MODULES = 10
MAX_GUIDE_DIRS = 8
READ_LIMIT = 12000


IMPORTANT_DOCS = [
    'README.md',
    'CLAUDE.md',
    'docs/ADR/README.md',
    'docs/ADR/ADR-CATALOG.md',
    'UML/README.md',
]


def stable_slug(text: str) -> str:
    base = sanitize_alias(text).lower() or 'item'
    return base[:80]



def tooltip_text(label: str, parts: list[str]) -> str:
    compact = [part.strip() for part in parts if str(part).strip()]
    return label if not compact else f"{label} â€” " + ' | '.join(compact[:5])



def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')[:READ_LIMIT]
    except UnicodeDecodeError:
        return path.read_text(encoding='utf-8', errors='ignore')[:READ_LIMIT]
    except FileNotFoundError:
        return ''



def _line_matches(text: str, pattern: str, limit: int = 6) -> list[str]:
    regex = re.compile(pattern, re.IGNORECASE)
    values: list[str] = []
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned and regex.search(cleaned):
            values.append(cleaned)
            if len(values) >= limit:
                break
    return values



def _summarize_document(repo_root: Path, rel_path: str) -> dict | None:
    path = repo_root / rel_path
    if not path.exists() or not path.is_file():
        return None
    text = _read_text(path)
    headings = [line.strip().lstrip('#').strip() for line in text.splitlines() if line.strip().startswith('#')][:8]
    quick_hits = _line_matches(text, r'quick start|usage|run|boot|skill|ollama|docker|host|architecture', limit=8)
    return {
        'path': rel_path,
        'headings': headings,
        'highlights': quick_hits,
    }



def _existing_paths(repo_root: Path, rel_paths: list[str]) -> list[str]:
    return [rel for rel in rel_paths if (repo_root / rel).exists()]



def _command_candidates(repo_root: Path) -> dict[str, str]:
    candidates: dict[str, str] = {}
    if (repo_root / '.claude/tools/boot_check.py').exists():
        candidates['boot_check'] = 'python .claude/tools/boot_check.py'
    if (repo_root / '.claude/tools/test_ollama.py').exists():
        candidates['ollama_probe'] = 'python .claude/tools/test_ollama.py'
    if (repo_root / '.claude/tools/skills/skill_runner.py').exists():
        candidates['legacy_skill_runner'] = 'python .claude/tools/skills/skill_runner.py <skill_name> [args]'
    if (repo_root / 'tools/skills/skill_runner.py').exists():
        candidates['legacy_skill_runner'] = 'python tools/skills/skill_runner.py --in request.json'
    if (repo_root / 'clockwork/server.py').exists():
        candidates['mcp_server'] = 'python -m clockwork.server'
    if (repo_root / 'run_tests.py').exists():
        candidates['tests'] = 'python run_tests.py'
    elif (repo_root / 'tests').exists():
        candidates['tests'] = 'pytest'
    return candidates



def _prerequisites(repo_root: Path, scan: RepoScan) -> list[str]:
    values = ['Run from the repository root so relative paths resolve correctly.']
    if any(module.language == 'python' for module in scan.modules):
        values.append('Python 3 is required for the Python tooling and the native skill implementations.')
    if (repo_root / '.claude/tools/boot_check.py').exists():
        values.append('The boot check should pass before relying on the generated review artifacts.')
    if (repo_root / '.claude/governance/ollama_integration.md').exists() or (repo_root / '.claude/tools/test_ollama.py').exists():
        values.append('Ollama is optional for the repository itself, but some higher-cost or delegated workflows may expect it to be reachable.')
    if (repo_root / 'Dockerfile').exists() or (repo_root / 'docker-compose.yml').exists() or (repo_root / 'docker-compose.yaml').exists():
        values.append('Container tooling is relevant when you want a repeatable hosting or execution environment.')
    return values



def _top_directories(scan: RepoScan) -> list[dict]:
    buckets: dict[str, dict] = {}
    for module in scan.modules:
        rel_dir = module.relative_dir or '.'
        parts = [part for part in Path(rel_dir).parts if part and part != '.']
        root_key = parts[0] if parts else '.'
        entry = buckets.setdefault(
            root_key,
            {
                'name': root_key,
                'module_count': 0,
                'class_count': 0,
                'function_count': 0,
                'line_count': 0,
                'languages': Counter(),
            },
        )
        entry['module_count'] += 1
        entry['class_count'] += len(module.classes)
        entry['function_count'] += module.function_count
        entry['line_count'] += module.line_count
        entry['languages'][module.language] += 1
    rows = []
    for value in buckets.values():
        rows.append(
            {
                'name': value['name'],
                'module_count': value['module_count'],
                'class_count': value['class_count'],
                'function_count': value['function_count'],
                'line_count': value['line_count'],
                'languages': dict(sorted(value['languages'].items())),
            }
        )
    rows.sort(key=lambda item: (-item['module_count'], -item['line_count'], item['name']))
    return rows[:MAX_GUIDE_DIRS]



def _hot_modules(scan: RepoScan) -> list[dict]:
    rows = []
    for module in scan.modules:
        score = (len(module.reverse_dependencies) * 4) + (len(module.internal_dependencies) * 3) + len(module.classes) + module.function_count
        rows.append(
            {
                'module_id': module.module_id,
                'relative_dir': module.relative_dir or '.',
                'language': module.language,
                'class_count': len(module.classes),
                'function_count': module.function_count,
                'line_count': module.line_count,
                'dependency_count': len(module.internal_dependencies),
                'reverse_dependency_count': len(module.reverse_dependencies),
                'score': score,
            }
        )
    rows.sort(key=lambda item: (-item['score'], item['module_id']))
    return rows[:MAX_GUIDE_MODULES]



def _relationship_notes(scan: RepoScan) -> list[str]:
    modules = sorted(
        scan.modules,
        key=lambda item: (len(item.reverse_dependencies), len(item.internal_dependencies), item.line_count),
        reverse=True,
    )
    notes: list[str] = []
    for module in modules[:MAX_GUIDE_RELATIONS]:
        if module.reverse_dependencies:
            notes.append(
                f"{module.module_id} has visible fan-in from {len(module.reverse_dependencies)} internal module(s), which makes it a likely shared dependency or coordination point."
            )
        elif module.internal_dependencies:
            notes.append(
                f"{module.module_id} mainly fans out to {len(module.internal_dependencies)} downstream internal module(s), so it looks more like an entry-edge or orchestrator module."
            )
        elif module.classes or module.function_count:
            notes.append(
                f"{module.module_id} appears relatively isolated in the detected dependency graph and can be reviewed as a local implementation island."
            )
    return notes[:MAX_GUIDE_RELATIONS]



def _find_related_modules(scan: RepoScan, names: list[str]) -> list[str]:
    wanted = [name.lower() for name in names if name]
    chosen: list[str] = []
    for module in scan.modules:
        lowered = module.module_id.lower()
        file_lower = module.file_path.lower()
        if any(name in lowered or name in file_lower for name in wanted):
            chosen.append(module.module_id)
    if not chosen:
        chosen = [item['module_id'] for item in _hot_modules(scan)[:4]]
    return list(dict.fromkeys(chosen))[:6]



def _find_related_directories(scan: RepoScan, names: list[str]) -> list[str]:
    roots = [item['name'] for item in _top_directories(scan)]
    chosen = [root for root in roots if any(name.lower() in root.lower() for name in names)]
    if not chosen:
        chosen = roots[:4]
    return chosen[:4]



def _supporting_files(repo_root: Path) -> list[dict]:
    rows = []
    for rel_path in IMPORTANT_DOCS:
        info = _summarize_document(repo_root, rel_path)
        if info:
            rows.append(info)
    extra = _existing_paths(
        repo_root,
        [
            'Dockerfile',
            'docker-compose.yml',
            'docker-compose.yaml',
            'requirements.txt',
            'pyproject.toml',
            '.claude/tools/boot_check.py',
            '.claude/tools/test_ollama.py',
            '.claude/tools/skills/skill_runner.py',
            'tools/skills/skill_runner.py',
            'clockwork/server.py',
        ],
    )
    for rel_path in extra:
        if rel_path.endswith('.md'):
            continue
        rows.append({'path': rel_path, 'headings': [], 'highlights': []})
    return rows



def build_how_it_works_payload(scan: RepoScan, context_payload: dict | None = None, repo_root: str | Path | None = None) -> dict:
    repo_root_path = Path(repo_root or scan.repo_root).resolve()
    commands = _command_candidates(repo_root_path)
    prerequisites = _prerequisites(repo_root_path, scan)
    top_dirs = _top_directories(scan)
    hot_modules = _hot_modules(scan)
    relationships = _relationship_notes(scan)
    support_files = _supporting_files(repo_root_path)

    if context_payload:
        directory_count = len(context_payload.get('directories', []))
        symbol_count = len(context_payload.get('symbols', []))
    else:
        directory_count = len(top_dirs)
        symbol_count = scan.class_count

    guide_defs = [
        {
            'id': 'technical_startup',
            'title': 'Technical startup and first run',
            'category': 'technical',
            'summary': 'How to start the repository tooling, verify the environment, and run the first review-oriented commands.',
            'related_directories': _find_related_directories(scan, ['.claude', 'claudeclockwork', 'tools']),
            'related_modules': _find_related_modules(scan, ['boot_check', 'skill_runner', 'cli', 'runtime']),
            'sections': [
                {
                    'title': 'What this guide covers',
                    'kind': 'paragraphs',
                    'items': [
                        'This guide focuses on the first technical touchpoints that are visible from the repository: boot checks, optional Ollama probes, and native skill entry points.',
                        'It does not assume one exact deployment stack. Instead it emits the entry points that are actually detectable in the current repository state.',
                    ],
                },
                {'title': 'Prerequisites', 'kind': 'checklist', 'items': prerequisites},
                {
                    'title': 'Recommended first steps',
                    'kind': 'steps',
                    'items': [
                        'Open a terminal in the repository root.',
                        'Run the boot check first when a boot-check script is present.',
                        'Probe optional Ollama connectivity only after the local boot checks are healthy.',
                        'Run either the legacy skill runner or the manifest-based CLI, depending on which entry point is present in the repository.',
                    ],
                },
                {
                    'title': 'Detected command candidates',
                    'kind': 'code',
                    'items': list(commands.values()) or ['No explicit command entry points were auto-detected. Review README.md and architecture documents manually.'],
                },
                {
                    'title': 'What should happen',
                    'kind': 'bullets',
                    'items': [
                        'The boot check should report pass/fail information rather than silently doing nothing.',
                        'A successful review-site build should create HTML, CSS, JS, and JSON artifacts under Docs/uml/review_site/.',
                        'The generated explorer should expose an overview page plus directory, module, symbol, and guide pages.',
                    ],
                },
            ],
        },
        {
            'id': 'hosting_and_publishing',
            'title': 'Hosting and publishing the review website',
            'category': 'technical',
            'summary': 'How to serve the generated UML review explorer locally or publish it as a static website.',
            'related_directories': _find_related_directories(scan, ['Docs', '.claude']),
            'related_modules': _find_related_modules(scan, ['cli', 'skill_runner', 'runtime']),
            'sections': [
                {
                    'title': 'Hosting model',
                    'kind': 'paragraphs',
                    'items': [
                        'The UML review explorer is generated as a static site, so it can be opened directly from disk or served by any static web server.',
                        'Because the site is documentation-like output, hosting is usually simpler than hosting the main runtime itself.',
                    ],
                },
                {
                    'title': 'Static hosting options',
                    'kind': 'bullets',
                    'items': [
                        'Open Docs/uml/review_site/index.html directly for quick local inspection.',
                        'Serve the generated folder with `python -m http.server` from inside the review_site directory for a small local web host.',
                        'Publish the generated folder to an internal docs host, static bucket, or Git-based pages workflow if that matches your repo process.',
                    ],
                },
                {
                    'title': 'Repository hints detected',
                    'kind': 'bullets',
                    'items': [
                        'Docker-related files were detected.' if any((repo_root_path / name).exists() for name in ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']) else 'No Docker-specific hosting files were detected at the top level.',
                        'A manifest CLI entry point was detected.' if 'manifest_skill_runner' in commands else 'No manifest CLI entry point was auto-detected.',
                        'A legacy skill runner entry point was detected.' if 'legacy_skill_runner' in commands else 'No legacy skill runner entry point was auto-detected.',
                    ],
                },
                {
                    'title': 'Expected hosted behavior',
                    'kind': 'steps',
                    'items': [
                        'The overview page should load without external CDNs.',
                        'Tooltip JSON should resolve from the local data/ directory.',
                        'Guide pages and entity pages should be reachable through normal hyperlink navigation.',
                    ],
                },
            ],
        },
        {
            'id': 'system_parts_and_relationships',
            'title': 'System parts and how they relate',
            'category': 'technical',
            'summary': 'A component-oriented guide describing the main repository areas, their roles, and the strongest visible relationships.',
            'related_directories': [item['name'] for item in top_dirs[:4]],
            'related_modules': [item['module_id'] for item in hot_modules[:6]],
            'sections': [
                {
                    'title': 'Main repository areas',
                    'kind': 'bullets',
                    'items': [
                        f"{item['name']}: {item['module_count']} module(s), {item['class_count']} class(es), {item['function_count']} function(s), {item['line_count']} line(s). Languages: {json.dumps(item['languages'])}" for item in top_dirs
                    ] or ['No major directories were derived from the repository scan.'],
                },
                {
                    'title': 'High-signal modules',
                    'kind': 'bullets',
                    'items': [
                        f"{item['module_id']}: inbound {item['reverse_dependency_count']}, outbound {item['dependency_count']}, classes {item['class_count']}, functions {item['function_count']}." for item in hot_modules
                    ] or ['No hotspot modules were derived from the repository scan.'],
                },
                {'title': 'Relationship notes', 'kind': 'bullets', 'items': relationships or ['No relationship notes were produced from the current dependency graph.']},
                {
                    'title': 'Supporting documents and entry files',
                    'kind': 'bullets',
                    'items': [
                        f"{item['path']}: headings {', '.join(item['headings'][:4]) or 'n/a'}" for item in support_files[:10]
                    ] or ['No supporting docs or entry files were detected.'],
                },
            ],
        },
        {
            'id': 'functional_operation',
            'title': 'Functional operation of the review suite',
            'category': 'functional',
            'summary': 'Explains what the analysis pipeline does, which prerequisites matter, and which outputs should appear after a successful run.',
            'related_directories': _find_related_directories(scan, ['Docs', '.claude', 'claudeclockwork']),
            'related_modules': _find_related_modules(scan, ['uml', 'runtime', 'cli', 'skill']),
            'sections': [
                {
                    'title': 'Functional pipeline',
                    'kind': 'steps',
                    'items': [
                        'The repository is scanned into a structured module-and-class model.',
                        'That scan is expanded into review context so directories, modules, and symbols gain local neighborhoods and tooltip text.',
                        'How-it-works guides are generated from the scan, detected entry points, and supporting repository documents.',
                        'A static review site is rendered from those payloads so the structure becomes navigable like a documentation website.',
                    ],
                },
                {
                    'title': 'What must be true first',
                    'kind': 'checklist',
                    'items': [
                        'The repository must be readable from the selected working directory.',
                        'Supported source files should be present in the scopes you want the explorer to cover.',
                        'The generation step needs write access for documentation artifacts under Docs/uml/.',
                    ],
                },
                {
                    'title': 'What the user should see',
                    'kind': 'bullets',
                    'items': [
                        'An overview page with repository-wide counts and navigation cards.',
                        'Directory, module, and symbol pages that keep local context visible.',
                        'Guide pages that explain startup, hosting, parts, and functional behavior in prose rather than only in graphs.',
                    ],
                },
            ],
        },
        {
            'id': 'preconditions_and_expected_outcomes',
            'title': 'Preconditions and expected outcomes',
            'category': 'functional',
            'summary': 'A compact expectation guide for what must be present before execution and what a healthy result should look like afterward.',
            'related_directories': _find_related_directories(scan, ['Docs', '.claude']),
            'related_modules': _find_related_modules(scan, ['boot_check', 'cli', 'skill', 'uml']),
            'sections': [
                {'title': 'Preconditions', 'kind': 'checklist', 'items': prerequisites + ['The target docs output directories must be writable.']},
                {
                    'title': 'Healthy outputs',
                    'kind': 'bullets',
                    'items': [
                        f"Repository scan summary should report modules, classes, and languages. Current scan saw {scan.module_count} module(s) and {scan.class_count} class(es).",
                        f"Context generation should produce directory, module, and symbol payloads. Current guide builder sees {directory_count} directory scope(s) and {symbol_count} symbol-level item(s).",
                        'Site generation should create a browsable index.html plus supporting subfolders for guides, directories, modules, symbols, assets, and data.',
                    ],
                },
                {
                    'title': 'Failure signals worth checking',
                    'kind': 'bullets',
                    'items': [
                        'Boot checks fail or never run.',
                        'The generated site has missing CSS, JS, or tooltip JSON files.',
                        'The explorer renders but large parts of the repository are absent because the working directory or include/exclude scope was wrong.',
                    ],
                },
            ],
        },
    ]

    guides = []
    tooltips: dict[str, str] = {}
    categories = Counter()
    for definition in guide_defs:
        slug = stable_slug(f"guide::{definition['id']}")
        definition['slug'] = slug
        definition['tooltip'] = tooltip_text(definition['title'], [definition['category'], definition['summary']])
        guides.append(definition)
        categories[definition['category']] += 1
        tooltips[f"guide::{definition['id']}"] = definition['tooltip']

    return {
        'summary': {
            'repo_root': str(repo_root_path),
            'guide_count': len(guides),
            'technical_guide_count': categories.get('technical', 0),
            'functional_guide_count': categories.get('functional', 0),
            'supporting_document_count': len(support_files),
            'module_count': scan.module_count,
            'class_count': scan.class_count,
        },
        'guides': guides,
        'supporting_files': support_files,
        'commands': commands,
        'tooltips': tooltips,
    }



def _render_section(section: dict) -> str:
    lines = [f"## {section['title']}", '']
    kind = section.get('kind', 'bullets')
    items = section.get('items', [])
    if kind == 'paragraphs':
        lines.extend(items)
    elif kind == 'code':
        lines.append('```bash')
        lines.extend(items)
        lines.append('```')
    elif kind == 'steps':
        for index, item in enumerate(items, start=1):
            lines.append(f"{index}. {item}")
    else:
        for item in items:
            lines.append(f"- {item}")
    lines.append('')
    return '\n'.join(lines)



def render_how_it_works_markdown(payload: dict) -> str:
    lines = [
        '# How It Works Guide Bundle',
        '',
        'This bundle explains technical startup, hosting, repository structure, functional flow, and expected outcomes.',
        '',
        '## Summary',
        '',
    ]
    for key, value in payload['summary'].items():
        lines.append(f"- **{key}**: {value}")
    lines.extend(['', '## Guides', ''])
    for guide in payload['guides']:
        lines.append(f"- **{guide['title']}** ({guide['category']}) â€” {guide['summary']}")
    lines.append('')
    return '\n'.join(lines)


def write_how_it_works_bundle(output_dir: Path, payload: dict) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    guides_dir = output_dir / 'guides'
    guides_dir.mkdir(parents=True, exist_ok=True)
    payload_json = output_dir / 'how_it_works.json'
    tooltips_json = output_dir / 'how_it_works_tooltips.json'
    summary_md = output_dir / 'README.md'

    write_json(payload_json, payload)
    write_json(tooltips_json, payload['tooltips'])
    write_text(summary_md, render_how_it_works_markdown(payload))

    guide_files: list[str] = []
    for guide in payload['guides']:
        lines = [
            f"# {guide['title']}",
            '',
            f"Category: **{guide['category']}**",
            '',
            guide['summary'],
            '',
        ]
        for section in guide['sections']:
            lines.append(_render_section(section))
        if guide.get('related_directories'):
            lines.extend(['## Related directories', ''])
            for item in guide['related_directories']:
                lines.append(f"- {item}")
            lines.append('')
        if guide.get('related_modules'):
            lines.extend(['## Related modules', ''])
            for item in guide['related_modules']:
                lines.append(f"- {item}")
            lines.append('')
        path = guides_dir / f"{guide['slug']}.md"
        write_text(path, '\n'.join(lines))
        guide_files.append(str(path))

    return {
        'payload_json': str(payload_json),
        'tooltips_json': str(tooltips_json),
        'summary_md': str(summary_md),
        'guide_markdown_files': guide_files,
        'guide_count': len(payload['guides']),
    }
