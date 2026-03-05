# Task: Refactor Bridge Scan

## Goal
Scan the repo for legacy markers and emit deterministic refactor suggestions.

## Steps
1) Create request `request_refactor_scan.json`:
```json
{
  "type": "skill_request_spec",
  "request_id": "bridge-001",
  "skill_id": "refactor_bridge_scan",
  "inputs": { "project_root": "." }
}
```
2) Run:
`python .claude/tools/skills/skill_runner.py --in request_refactor_scan.json`

## Acceptance
- Outputs list found markers + suggestions
