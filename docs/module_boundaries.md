# Module Boundaries (Phase 52)

Domain packages and public vs internal separation.

## Domain packages

| Package | Role | Public API |
|---------|------|------------|
| `claudeclockwork.core` | Base types, executor, gates, security | Internal |
| `claudeclockwork.cli` | CLI entrypoints | Via `clockwork` script only |
| `claudeclockwork.cas` | Content-addressed store | Internal |
| `claudeclockwork.workgraph` | Work graph runner, cache | Internal |
| `claudeclockwork.plugins` | Plugin loader, registry, signing | Internal |
| `claudeclockwork.scheduler` | Job queue, telemetry | Internal |
| `claudeclockwork.optimizer` | Cost model, calibration | Internal |
| `claudeclockwork.workers` | Dispatcher, local worker | Internal |
| `claudeclockwork.workspace` | Federation, bundles, policy | Internal |

Public surface is defined in `Docs/public_api.md`. All other modules are internal.

## Refactor plan

- Incremental: one package at a time; no big-bang.
- Rollbackable: each step is a single PR; revert restores previous state.
