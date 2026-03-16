# First-Run Wizard (Phase 28)

Running `clockwork first-run` (or `python -m claudeclockwork.cli first-run`) is **idempotent**: safe to run multiple times.

## What it does

- Creates `.clockwork_runtime/` with subdirs: telemetry, reports, evidence, redacted_exports, eval/results, eval/baselines, knowledge, audit.
- Writes minimal runtime config if missing.
- Checks optional dependencies (LocalAI: sentence_transformers, whisper) and reports warnings only.

## When to run

- After cloning the repo or installing Clockwork.
- Before running `env-check` or skills that write to the runtime root.

## Permissions

Requires write access to the project root to create `.clockwork_runtime/`.
