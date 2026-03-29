# UML Skill Pack for ClaudeClockwork

This package adds native manifest-based UML analysis skills that scan a repository and generate UML-friendly artifacts in multiple scopes.

## Included skills

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

## Output formats

The skills generate text-based artifacts so they remain dependency-free:

- PlantUML: `*.puml`
- Mermaid: `*.mmd`
- Markdown indexes: `README.md`
- JSON summaries/catalogs: `*.json`

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
- `.claude/skills/analysis/uml_scope_catalog/...`
- `.claude/skills/analysis/uml_diagram_generate/...`
- `.claude/skills/analysis/uml_focus_bundle/...`
- `.claude/skills/analysis/uml_repo_bundle/...`

## Suggested usage order

1. Run `uml_scope_catalog`
2. Run `uml_repo_bundle`
3. Use `uml_diagram_generate` for a specific package/module/class
4. Use `uml_focus_bundle` when a local subsystem needs deeper inspection

## Example intents

- "Catalog this repo for UML scopes"
- "Generate a UML bundle for the whole repository"
- "Generate UML diagrams for the module `claudeclockwork.core.registry.skill_registry`"
- "Focus on the symbol `SkillRegistry` and expand its neighborhood"
- "Generate UML diagrams for the directory `claudeclockwork/core`"

## Notes

- The skills are read-only toward source code and write only documentation artifacts.
- The diagrams are intentionally bounded so large repositories stay navigable.
- Sequence diagrams are not generated automatically, because reliable sequence recovery usually needs runtime traces or stronger semantic analysis.
