# QA Gate Policy (v17.6)

## Rule
Before **any** risky work (refactors, routing changes, schema edits, tool changes), run the hard gate:
- `qa_gate` (tool-first)

## Gate definition
The gate is PR-blocking and deterministic:
- repo validation (links + JSON validity + optional secret scan)
- contract drift sentinel (schemas/examples/tasks)
- team topology verification (required agent files)
- SSoT doc reference resolution (backticked path semantics)
- semantic drift check (registry ↔ runner mismatch)

## Extended QA
Extended mode may run additional suites (`schema_batch_validate`, evidence bundle, redaction). Use it for:
- nightly builds
- release cuts

## Failure protocol
If the gate fails:
1) stop feature work
2) fix drift
3) re-run gate
## SSoT scope
By default the gate runs in **claude_only** mode (so `.claude-only` distributions are green out-of-the-box):
- `<PROJECT_ROOT>/...` references are treated as external and skipped (except `<PROJECT_ROOT>/.claude/...`).

To enforce full project checks in a real repo, run:
- `qa_gate` with `ssot_scope=full` **or** `verify_project_root=true`
- optional: `verify_legacy=true` to also validate `.claude/...` references

