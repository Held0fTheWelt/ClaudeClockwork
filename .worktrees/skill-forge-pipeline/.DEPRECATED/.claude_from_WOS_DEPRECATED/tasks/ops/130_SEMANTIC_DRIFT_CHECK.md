# Task: Semantic Drift Check

## Goal
Run semantic drift checks (registry ↔ runner, SSoT paths, contracts).

## Steps
1) Create request `request_semantic_drift.json`:
```json
{
  "type": "skill_request_spec",
  "request_id": "drift-001",
  "skill_id": "drift_semantic_check",
  "inputs": { "claude_root": ".claude" }
}
```
2) Run:
`python .claude/tools/skills/skill_runner.py --in request_semantic_drift.json`

## Acceptance
- `status=ok`
