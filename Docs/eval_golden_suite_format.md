# Eval Golden Suite Format (Phase 25)

Golden suites define deterministic inputs and expected outputs for capability evaluation.

## Layout

- **Location:** `eval/golden_suites/` (or `.claude/eval/golden_suites/`).
- **Per capability:** e.g. `embed_text/`, `audio_asr/`.
- **Contents:** `inputs.json` (or references to input files), `expected.json` (exact or tolerance-based), optional `scoring.yaml` (quality proxy).

## Inputs

- Inline JSON or paths to files (e.g. `inputs: [{"text": "hello"}]` or `inputs_ref: "fixtures/embed_1.json"`).
- Keep suites small and repo-friendly; use hashed references for large assets if needed.

## Expected outputs

- Exact match (e.g. `status: ok`) or tolerance (e.g. `embedding_dim: {min: 1, max: 1024}`).
- Scoring function: optional quality proxy (e.g. cosine similarity to reference).

## Runnability

Suites are deterministic and runnable locally and in CI (mocked runners when dependencies are missing).
