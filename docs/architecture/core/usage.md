# Clockwork Core Usage

This page explains how to use the live Clockwork core: the Python package, MCP
server, UML/review bundle builders, documentation gate, and local pipeline
tools exposed by the server.

## Install

Core tools and tests:

```bash
python -m pip install -e ".[dev]"
```

Core tools, tests, and local model pipelines:

```bash
python -m pip install -e ".[dev,local]"
```

## Run Tests

Full suite:

```bash
python -m pytest tests/ -q
```

Architecture documentation gate only:

```bash
python -m pytest tests/gates -q
```

## Run The MCP Server

Clockwork is registered in `.mcp.json`:

```json
{
  "mcpServers": {
    "clockwork": {
      "command": "python",
      "args": ["-m", "clockwork.server"]
    }
  }
}
```

Manual stdio server run:

```bash
python -m clockwork.server
```

## MCP Tool Reference

| Tool | Main arguments | Use when |
|---|---|---|
| `uml_scope_catalog` | `repo_root`, `output_dir`, `include_tests` | You need an inventory of modules, classes, languages, and directories. |
| `uml_repo_bundle` | `repo_root`, `output_dir`, `include_tests`, `max_directory_bundles` | You want repository-wide component, dependency, and class diagrams. |
| `uml_focus_bundle` | `repo_root`, `scope_kind`, `target`, `neighbor_depth`, `include_methods` | You want diagrams for one directory, module, or symbol plus nearby dependencies. |
| `uml_diagram_generate` | `repo_root`, `scope_kind`, `target`, `include_methods`, `neighbor_depth` | You want a compact diagram set for a selected scope. |
| `review_context_build` | `repo_root`, `output_dir`, `neighbor_depth`, `max_neighbors` | You need JSON context for review tools or custom explorers. |
| `review_site_build` | `repo_root`, `output_dir`, `site_title`, `include_guides` | You want a static HTML review explorer. |
| `how_it_works_build` | `repo_root`, `output_dir`, `neighbor_depth`, `max_neighbors` | You want generated how-it-works guide content. |
| `architecture_gate` | `repo_root` | You want the gate result through MCP instead of pytest. |
| `local_health` | none | You want to know whether Ollama is reachable. |
| `local_brief` | `task`, `model` | You want a short local-model work brief. |
| `local_draft_review_refine` | `task`, `model` | You want a local draft->review->refine loop. |

## Python API Examples

Generate a repository bundle:

```bash
python -c "from clockwork.tools.bundles import build_repo_bundle; print(build_repo_bundle('.')['output_dir'])"
```

Generate a focused bundle for `clockwork/tools`:

```bash
python -c "from clockwork.tools.bundles import build_focus_bundle; print(build_focus_bundle('.', 'directory', 'clockwork/tools')['output_dir'])"
```

Generate a static review site:

```bash
python -c "from clockwork.tools.bundles import build_review_site_bundle; print(build_review_site_bundle('.', site_title='Clockwork Review')['output_dir'])"
```

Run the architecture gate from Python:

```bash
python -c "from clockwork.tools.gates import check_architecture_docs; print(check_architecture_docs('.'))"
```

Run a local brief:

```bash
python -c "from clockwork.pipelines.briefs import run_brief; print(run_brief('Summarize the Clockwork architecture'))"
```

## Output Locations

Default generated outputs go under `UML/generated/`:

| Builder | Default directory |
|---|---|
| `build_scope_catalog` | `UML/generated/catalog/` |
| `build_repo_bundle` | `UML/generated/repo_bundle/` |
| `build_focus_bundle` | `UML/generated/focus_<scope>_<target>/` |
| `generate_diagrams` | `UML/generated/diagrams_<scope>/` |
| `build_review_context_bundle` | `UML/generated/review_context/` |
| `build_review_site_bundle` | `UML/generated/review_site/` |
| `build_how_it_works_bundle` | `UML/generated/how_it_works/` |

`UML/generated/` is gitignored. Curated diagrams belong under
`UML/Components/<slug>/`.

## Local Pipeline Behavior

Local tools use `clockwork.yaml` and `OllamaClient`.

If Ollama is reachable, local calls return `status: ok` plus generated content.
If not, they return `status: local_backend_unavailable`. This is intentional:
deterministic tools must keep working even when local models are offline.

Explicitly forbidden models raise `ForbiddenModelError`; the forbidden list is
stored in `clockwork.yaml`.

## Adding A New Tool

1. Add plain library logic under `clockwork/tools/` or `clockwork/pipelines/`.
2. Add or extend unit tests under `tests/clockwork/`.
3. Expose the tool in `clockwork/server.py`.
4. If the change is structural, add an ADR and update the owning SAD.
5. If the component view changes, update the relevant `UML/Components/<slug>/`
   package.
6. Run `python -m pytest tests/ -q`.
