# UML Skill Pack for ClaudeClockwork

This package adds native manifest-based UML analysis and review skills that scan a repository, generate UML-friendly artifacts in multiple scopes, and build a navigable static review website.

## Included skills

### Core scope and diagram skills

- `uml_scope_catalog`
  - scans the repository
  - inventories directories, modules, classes, and dependency hints
  - writes `Docs/uml/catalog/`

- `uml_diagram_generate`
  - generates diagrams for one selected scope
  - supports `repo`, `directory`, `module`, and `symbol`
  - writes focused diagram sets to `Docs/uml/scopes/<scope>/`

- `uml_focus_bundle`
  - builds a deeper local bundle around one directory, module, or symbol
  - expands incoming and outgoing dependency neighborhoods
  - writes to `Docs/uml/focus/<scope>/`

- `uml_repo_bundle`
  - generates a repository-wide overview bundle plus major directory slices
  - writes to `Docs/uml/repo_bundle/`

### Review explorer skills

- `uml_review_context_build`
  - builds a UML review context bundle
  - creates directory/module/symbol context cards and tooltip payloads
  - writes to `Docs/uml/review_context/`

- `uml_review_site_build`
  - generates a static UML review website
  - creates overview, directory, module, and symbol pages
  - uses tooltip-backed navigation and per-page context previews
  - writes to `Docs/uml/review_site/`

- `uml_review_bundle`
  - runs the context build, how-it-works guide build, and review site build in one pass
  - is the most direct entry point for a full review website

- `repo_how_it_works_build`
  - generates technical and functional guide pages
  - explains startup, hosting, parts, relationships, prerequisites, and expected outcomes
  - writes to `Docs/uml/how_it_works/`

- `uml_review_knowledge_bundle`
  - produces context, guides, and review site artifacts as one combined knowledge bundle

## Output formats

The skills generate dependency-light artifacts:

- PlantUML: `*.puml`
- Mermaid: `*.mmd`
- Markdown indexes: `README.md`
- JSON summaries/catalogs: `*.json`
- Static website files: `*.html`, `*.css`, `*.js`
- Technical and functional guide bundles: `how_it_works.json`, `guides/*.md`

## Supported code understanding

Best support:

- Python AST-based import/class extraction
- C/C++ include/class heuristics
- TypeScript / JavaScript import/class heuristics
- Java / C# / Go / Rust / PHP via lightweight regex heuristics

## Installation

Merge this package into the repository root so the following paths exist:

- `.claude/skills/analysis/__init__.py`
- `.claude/skills/analysis/uml_shared.py`
- `.claude/skills/analysis/uml_review_shared.py`
- `.claude/skills/analysis/uml_scope_catalog/...`
- `.claude/skills/analysis/uml_diagram_generate/...`
- `.claude/skills/analysis/uml_focus_bundle/...`
- `.claude/skills/analysis/uml_repo_bundle/...`
- `.claude/skills/analysis/uml_review_context_build/...`
- `.claude/skills/analysis/uml_review_site_build/...`
- `.claude/skills/analysis/uml_review_bundle/...`

## Suggested usage order

1. Run `uml_scope_catalog`
2. Run `uml_repo_bundle`
3. Run `uml_review_context_build`
4. Run `uml_review_site_build`
5. Run `repo_how_it_works_build` when you want standalone technical and functional guides
6. Or run `uml_review_bundle` / `uml_review_knowledge_bundle` directly for a full explorer output

## Example intents

- "Catalog this repo for UML scopes"
- "Generate a UML bundle for the whole repository"
- "Focus on the symbol `SkillRegistry` and expand its neighborhood"
- "Build the UML review context for this repo"
- "Create a UML review website for the current codebase"
- "Generate the full UML review bundle including the website"

## Notes

- The review context skill is intentionally narrowly named for this UML review use case.
- The static review website is offline-capable and does not depend on external CDNs.
- Tooltips are driven by generated JSON context rather than hardcoded page text.
- The website uses lightweight SVG context previews rather than heavyweight external graph renderers.
- The skills are read-only toward source code and write only documentation artifacts.
