# Report vs Runtime Policy (Phase 19)

## Rule

- **`.report/`** — Curated, human-facing summaries only. Use for final reports, dashboards, and exports that are explicitly published or shared.
- **`.clockwork_runtime/`** — All machine-generated runtime outputs: telemetry, eval results, evidence, ledgers, intermediate reports, and redacted exports.

## Layout reference

| Output type | Location |
|-------------|----------|
| Raw telemetry (JSONL) | `.clockwork_runtime/telemetry/` |
| Derived machine reports | `.clockwork_runtime/reports/` |
| Evidence / artifacts | `.clockwork_runtime/evidence/` |
| Redacted export bundles | `.clockwork_runtime/redacted_exports/` |
| Eval results and baselines | `.clockwork_runtime/eval/` |
| Knowledge writes, ledgers | `.clockwork_runtime/knowledge/` |
| Human-facing reports | `.report/` (only when explicitly exported here) |

## Allowed writes into `.report/`

Only a deterministic exporter (or explicit user request) should copy or redact runtime outputs into `.report/`. Skills must not write raw runtime outputs directly into `.report/`; write to `.clockwork_runtime/` and optionally export a summary to `.report/` when requested.
