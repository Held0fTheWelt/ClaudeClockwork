# Clockwork

ADR/SAD/UML-anchored orchestration toolkit: Claude Code as orchestrator, a
Python MCP tool server for deterministic architecture tooling (UML
generation, review bundles, documentation gates), and LangGraph pipelines
for local Ollama models.

## Install

```bash
python -m pip install -e ".[dev]"        # core + tests
python -m pip install -e ".[dev,local]"  # + local-model pipelines
```

## Use

Register the MCP server via the checked-in `.mcp.json` (Claude Code picks it
up automatically) or run `python -m clockwork.server` for any MCP client.

## Architecture

Decisions live in `docs/ADR/` (catalog: `docs/ADR/ADR-CATALOG.md`),
consolidated into arc42 SADs under `docs/architecture/`, with code-aligned
UML in `UML/Components/`. Consistency is enforced by
`tests/gates/test_architecture_documentation_gate.py`.

History: the pre-reboot system (v17) is archived at git tag `v17-archive`.
