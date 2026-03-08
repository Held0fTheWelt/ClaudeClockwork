# .claude-performance/ — Curated Performance Index

`.claude-performance/` is a **curated** directory. It contains only:
- `README.md` — this file (human-facing description)
- `reviews/` — example/template stubs (non-runtime)
- `charts/` — directory marker only (`.gitkeep`)

## Runtime Outputs (NOT stored here)

Raw telemetry and machine-generated reports go to the **runtime root**, never here:

| Output type | Runtime location |
|-------------|-----------------|
| JSONL token event logs | `.clockwork_runtime/performance/events/` |
| Budget/perf reports | `.clockwork_runtime/performance/reports/` |
| PNG charts | `.clockwork_runtime/performance/charts/` |

## Event Format

Each line in `.clockwork_runtime/performance/events/*.jsonl` is a `budget_event`:
```json
{"ts": "<ISO8601>", "run_id": "...", "role": "...", "model": "...", "task": "...", "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
```

## Written by

- `.claude/tools/telemetry_writer.py`
- `.claude/tools/token_event_autologger.py`
- `.claude/tools/skills/budget_analyze.py`

## Schemas

- `.claude/contracts/schemas/budget_event.schema.json`
- `.claude/contracts/schemas/budget_report.schema.json`
- `.claude/contracts/schemas/efficiency_review.schema.json`

## Curated Summary Policy (Phase 74)

If a human-facing performance summary is needed for sharing:

1. Generate it from runtime data explicitly (do NOT auto-write into `.report/`)
2. Hand-review and redact (no host paths, no run-specific metadata)
3. Commit to `Docs/` with an explicit curated filename

**Do NOT** write runtime or machine-generated outputs into `.report/performance/`.
`.report/` is curated-only — only explicitly exported, human-reviewed summaries belong there.

See `Docs/report_vs_runtime_policy.md` for the canonical policy.

## Notes

- All event files are **append-only**. Never delete or truncate mid-run.
- `.claude-performance/reports/` and `.claude-performance/events/` are gitignored
  (Phase 69). They are generated locally and never committed.
- Gate: `perf_artifact_gate` (DR-003) blocks committed machine-run files here.
- Gate: `doc_policy_consistency_gate` (DR-007, Phase 74) blocks conflicting instructions.
