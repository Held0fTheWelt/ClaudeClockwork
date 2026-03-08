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

---

## Phase 69 — `.claude-performance/` Policy

**Decision: Option A — Curated-only index.**

`.claude-performance/` is a **curated** directory. It must contain only:
- `README.md` — human-facing description of the telemetry structure
- `reviews/` — example/template stubs (non-runtime)
- `charts/.gitkeep` — directory marker

**What is NOT allowed in `.claude-performance/`:**
- `reports/` — machine-generated budget/performance reports (go to `.clockwork_runtime/performance/reports/`)
- `events/` — raw JSONL telemetry logs (go to `.clockwork_runtime/performance/events/`)
- Any timestamped machine-run output (`run-unknown`, `run-*`, `*_report_*.json`, etc.)

**Why these existed:**
`budget_analyze.py`, `performance_finalize.py`, and `performance_toggle.py` defaulted to
writing into `.claude-performance/reports/`. This was a naming confusion — the directory name
implies telemetry, but it was being used as a runtime output sink. The default paths have been
removed from git tracking via `.gitignore` (Phase 69).

**Gate:** `perf_artifact_gate` (Phase 69) blocks committed machine-run files under `.claude-performance/`.

**Drift prevention:** `.claude-performance/reports/` and `.claude-performance/events/` are
added to `.gitignore`. They are generated locally and never committed.
