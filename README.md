# Clockwork

Clockwork is an ADR/SAD/UML-anchored orchestration toolkit for Claude Code and
local model workflows. It keeps the agent-facing layer thin, puts deterministic
repository analysis behind a Python MCP server, and records architectural
decisions in versioned documents that are checked by tests.

The current codebase is the 2026-07 reboot of the older ClaudeClockwork v17
system. The old system is preserved at git tag `v17-archive`; the live system is
the `clockwork/` Python package plus the documentation corpus in `docs/` and
`UML/`.

## What It Does

- Exposes an MCP server for Claude Code or any MCP client.
- Scans repositories and generates UML-friendly bundles.
- Builds review context bundles and a static review explorer site.
- Enforces ADR/SAD/UML documentation consistency through pytest gates.
- Provides optional local Ollama workflows for brief generation and
  draft->review->refine loops with graceful degradation.

Clockwork is not a replacement for Claude Code. Claude remains the
orchestrator; Clockwork supplies deterministic tools and documented structure.

## Quick Start

Install the package in editable mode:

```bash
python -m pip install -e ".[dev]"
```

Install local-model pipeline dependencies as well:

```bash
python -m pip install -e ".[dev,local]"
```

Run the test suite:

```bash
python -m pytest tests/ -q
```

Run the MCP server:

```bash
python -m clockwork.server
```

Claude Code can also discover it from the checked-in `.mcp.json`.

## Repository Map

| Path | Purpose |
|---|---|
| `clockwork/server.py` | FastMCP stdio server exposing Clockwork tools. |
| `clockwork/tools/` | Deterministic repository analysis, UML bundle builders, review-site builders, and documentation gates. |
| `clockwork/pipelines/` | Optional local Ollama workflows using LangGraph. |
| `clockwork.yaml` | Local Ollama runtime defaults and GPU-first model constraints. |
| `.mcp.json` | MCP registration for the local Clockwork server. |
| `.claude/agents/clockwork-architect.md` | Thin Claude Code agent for maintaining the ADR/SAD/UML corpus. |
| `docs/ADR/` | Architecture Decision Records and the searchable ADR catalog. |
| `docs/architecture/` | arc42-style software architecture documents and usage notes. |
| `docs/superpowers/` | Reboot spec and implementation plans retained as project history. |
| `UML/Components/` | Curated, code-aligned UML packages with traceability tables. |
| `UML/generated/` | Generated analysis output; intentionally gitignored. |
| `tests/clockwork/` | Unit and integration tests for the package. |
| `tests/gates/` | Repo-level documentation gate tests. |

## MCP Tools

The server currently exposes 11 tools:

| Tool | What it returns or writes |
|---|---|
| `uml_scope_catalog` | Repository inventory as JSON and Markdown. |
| `uml_repo_bundle` | Repository-wide PlantUML/Mermaid diagrams and summary files. |
| `uml_focus_bundle` | Focused diagrams around a directory, module, or symbol. |
| `uml_diagram_generate` | Component, dependency, and class diagrams for a selected scope. |
| `review_context_build` | Machine-readable review context and tooltip data. |
| `review_site_build` | Static HTML review explorer site. |
| `how_it_works_build` | Generated guide bundle explaining repository operation. |
| `architecture_gate` | ADR/SAD/UML consistency check as an MCP result. |
| `local_health` | Local Ollama availability and configured default model. |
| `local_brief` | Short local-model work brief, or graceful unavailable status. |
| `local_draft_review_refine` | LangGraph draft->review->refine result, or graceful unavailable status. |

Detailed examples live in
[`docs/architecture/core/usage.md`](docs/architecture/core/usage.md).

## Documentation System

Clockwork uses three documentation layers:

1. ADRs decide changes. Start with
   [`docs/ADR/ADR-CATALOG.md`](docs/ADR/ADR-CATALOG.md).
2. SADs consolidate current architecture. Start with
   [`docs/architecture/README.md`](docs/architecture/README.md).
3. UML packages show code-aligned views with traceability. Start with
   [`UML/README.md`](UML/README.md).

The documentation gate checks that ADRs are cataloged, ADRs contain Mermaid
diagrams, SADs own cataloged ADRs, linked UML packages exist, and component UML
packages contain `README.md` and `TRACEABILITY.md`.

Run it directly:

```bash
python -m pytest tests/gates -q
```

## Local Ollama Pipelines

Local model settings live in `clockwork.yaml`.

Defaults:

- backend: `http://127.0.0.1:11434`
- default model: `qwen3:8b`
- fallback model: `phi4`
- forbidden explicit models: 32B/70B/72B class models listed in
  `clockwork.yaml`

If Ollama is not reachable, local tools return
`{"status": "local_backend_unavailable"}` instead of blocking deterministic
work.

## Development Workflow

Before structural changes:

1. Search `docs/ADR/ADR-CATALOG.md`.
2. Read the owning SAD under `docs/architecture/`.
3. Update the relevant UML package when code structure changes.
4. Run:

```bash
python -m pytest tests/ -q
```

If you touch ADRs, SADs, or UML packages, run the gate too:

```bash
python -m pytest tests/gates -q
```

## Common Tasks

Generate a repository UML bundle:

```bash
python -c "from clockwork.tools.bundles import build_repo_bundle; print(build_repo_bundle('.')['output_dir'])"
```

Generate a review site:

```bash
python -c "from clockwork.tools.bundles import build_review_site_bundle; print(build_review_site_bundle('.')['output_dir'])"
```

Check architecture docs from Python:

```bash
python -c "from clockwork.tools.gates import check_architecture_docs; print(check_architecture_docs('.'))"
```

Check local model availability:

```bash
python -c "from clockwork.pipelines.runtime import OllamaClient; print(OllamaClient().is_available())"
```

## Troubleshooting

- `python3` is not available on some Windows hosts. Use `python`.
- `UML/generated/` can be deleted and regenerated; do not commit it.
- If the architecture gate fails, read the violation text first. It usually
  points to a missing ADR catalog row, broken relative link, missing Mermaid
  block, or missing UML package.
- If local tools report `local_backend_unavailable`, deterministic tools still
  work. Start Ollama or continue without local-model assistance.

## Status

The rebooted system currently has:

- 11 MCP tools
- 29 tests
- ADRs `ADR-CW-0001` through `ADR-CW-0007`
- two accepted SADs: core and local pipelines
- two curated UML component packages: `clockwork-core` and
  `clockwork-pipelines`
