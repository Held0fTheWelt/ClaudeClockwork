# Clockwork Documentation Map

This directory is the durable documentation entry point for the live Clockwork
architecture. Use it when you need to understand what exists, why it exists, and
where to change it.

## Where To Start

| Need | Read |
|---|---|
| What decisions define the system? | [`../ADR/ADR-CATALOG.md`](../ADR/ADR-CATALOG.md) |
| How is the MCP/tooling core structured? | [`core/architecture.md`](core/architecture.md) |
| How do I use the tools? | [`core/usage.md`](core/usage.md) |
| How do local Ollama pipelines work? | [`local-pipelines/architecture.md`](local-pipelines/architecture.md) |
| What diagrams are maintained? | [`../../UML/README.md`](../../UML/README.md) |
| What changed during the reboot? | [`../superpowers/plans/2026-07-10-reboot-overview.md`](../superpowers/plans/2026-07-10-reboot-overview.md) |

## Documentation Types

| Type | Directory | Role |
|---|---|---|
| ADR | `docs/ADR/` | Captures decisions and tradeoffs. Every structural change gets one when it changes architecture. |
| SAD | `docs/architecture/*/architecture.md` | Consolidates the current architecture for an area. Each SAD owns one or more ADRs. |
| Usage note | `docs/architecture/*/usage.md` | Explains how to operate the area without changing the decision record. |
| UML package | `UML/Components/<slug>/` | Curated diagrams plus traceability back to code and tests. |
| Superpowers history | `docs/superpowers/` | Reboot specs and plans. Useful for history, not normative runtime docs. |

## Current Architecture Areas

### Core

The core area covers `clockwork/server.py` and `clockwork/tools/`.

Read:

- [`core/architecture.md`](core/architecture.md)
- [`core/usage.md`](core/usage.md)
- [`../../UML/Components/clockwork-core/README.md`](../../UML/Components/clockwork-core/README.md)

### Local Pipelines

The local pipelines area covers `clockwork/pipelines/`, `clockwork.yaml`, and
the three local MCP tools.

Read:

- [`local-pipelines/architecture.md`](local-pipelines/architecture.md)
- [`../../UML/Components/clockwork-pipelines/README.md`](../../UML/Components/clockwork-pipelines/README.md)

## Keeping Docs Healthy

Run the documentation gate:

```bash
python -m pytest tests/gates -q
```

The gate checks ADR registration, ADR Mermaid diagrams, SAD frontmatter,
SAD-owned ADR references, local Markdown links inside ADR/SAD files, and
required UML package files.

When code structure changes, regenerate analysis output into `UML/generated/`,
then curate the relevant `UML/Components/<slug>/` package:

```bash
python -c "from clockwork.tools.bundles import build_repo_bundle; print(build_repo_bundle('.')['output_dir'])"
```

Do not commit `UML/generated/`; commit only curated UML packages.
