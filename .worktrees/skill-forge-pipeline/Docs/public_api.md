# Public API Boundary Map

> Only symbols listed here are part of the versioned public API. All other modules are internal.

## Public package: `claudeclockwork`

**Public surface (stable, SemVer-bound):**

- `claudeclockwork.__version__` — str, e.g. `"0.1.0"`
- `claudeclockwork` — package; no other top-level attributes are public.

**Public entrypoints:**

- CLI: `python -m claudeclockwork.cli` (see `Docs/cli_contract.md`)
- Programmatic: use only the symbols explicitly listed in this document.

## Internal (not public)

All subpackages and modules are **internal** unless listed above or in a future update to this document:

- `claudeclockwork.bridge`
- `claudeclockwork.cas`
- `claudeclockwork.cli.*` (implementation details)
- `claudeclockwork.core.*`
- `claudeclockwork.eval`
- `claudeclockwork.legacy`
- `claudeclockwork.localai`
- `claudeclockwork.mcp`
- `claudeclockwork.optimizer`
- `claudeclockwork.plugins`
- `claudeclockwork.router`
- `claudeclockwork.runtime`
- `claudeclockwork.telemetry`
- `claudeclockwork.workgraph`
- `claudeclockwork.workers`
- `claudeclockwork.workspace`
- `claudeclockwork.kb`

Consumers must not rely on internal modules; they may change without a major version bump.

## Verification

Run the public surface gate to detect accidental expansion:

```bash
python -m claudeclockwork.core.gates.public_surface_gate
```
