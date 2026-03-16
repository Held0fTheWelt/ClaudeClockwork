# Test Pyramid (Phase 53)

## Structure

- **tests/unit/** — Fast, no I/O. Deterministic stubs. Run on every PR.
- **tests/integration/** — Multiple components; temp dirs OK. Run on PR or nightly.
- **tests/e2e/** — Full CLI/pipeline. Run on nightly or on-demand.

## PR vs nightly

- **PR:** `pytest tests/ tests/unit/ tests/integration/` (exclude e2e if slow).
- **Nightly:** Full suite including `tests/e2e/`.

## Deterministic stubs

Work graph runner stubs node execution (no real skill/gate calls). Cost model, scheduler, and plugin validator use in-memory or temp paths. Demos use stubbed graphs.
