# limitation_harvest_scan

Pre-step for DocForge: scan the repo for **Limitations**, **Non-Goals**, **Future Work** and especially an **Expected-but-missing** list.

## Why
Writers often forget to state what users *assume* exists. This scan produces a writer-ready list for:
- Expectation traps
- Non-Goals
- Conceivable / Future Work

## Skill ID
- `limitation_harvest_scan`

## Usage
See `.claude/contracts/examples/limitation_harvest_scan.skill_request.example.json`.

## Outputs
- JSON + Markdown report under `.llama_runtime/knowledge/writes/limitation_harvest/`
