# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What This Repository Is

**Clockwork** - an ADR/SAD/UML-anchored orchestration toolkit: a thin Claude
Code layer, a Python MCP tool server (`clockwork/`), and (Phase 3+) LangGraph
pipelines for local Ollama models. Rebooted 2026-07 (see ADR-CW-0001); the
v17 era is archived at git tag `v17-archive`.

## Execution Protocol

1. Search `docs/ADR/ADR-CATALOG.md` before structural changes.
2. Read the owning SAD under `docs/architecture/` before changing
   cross-cutting behavior; follow its `uml-package` link for diagrams.
3. Every structural decision: ADR + catalog row in the same change
   (`docs/ADR/adr-template.md`), with at least one Mermaid diagram.
4. The gate is normative: `python -m pytest tests/gates -q` must be green
   before any commit that touches docs/ADR, docs/architecture, or UML/.

## Commands

```bash
python -m pytest tests/ -v          # full suite
python -m pytest tests/gates -q     # architecture documentation gate
python -m clockwork.server          # MCP server (stdio); registered in .mcp.json
python -c "from clockwork.tools.bundles import build_repo_bundle; build_repo_bundle('.')"
```

## Structure

- `clockwork/` - package: `server.py` (FastMCP), `tools/` (UML suite,
  review builder, gates), `pipelines/` (local-model graphs)
- `docs/ADR/` + `docs/architecture/` - decision corpus (normative)
- `UML/Components/<slug>/` - curated diagrams + TRACEABILITY per component;
  `UML/generated/` is tool output (gitignored)
- `.claude/agents/clockwork-architect.md` - corpus maintenance agent
- `docs/superpowers/` - specs and plans history

## Rules

- Filesystem is case-insensitive: never create paths differing only by case.
- Local-model unavailability degrades gracefully; deterministic tools never
  depend on Ollama (no FREEZE semantics - ADR-CW-0002).
- New capabilities = MCP tools with unit tests, not markdown processes.
