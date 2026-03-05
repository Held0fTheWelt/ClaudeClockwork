# Task: Run Hard QA Gate

## Goal
Run the **PR-blocking QA gate** and stop on failure.

## Inputs
- Project root (default: `<PROJECT_ROOT>/.`)
- Claude clock root (default: `.claude`)

## Steps
1) Create a request file `request_qa_gate.json`:
```json
{
  "type": "skill_request_spec",
  "request_id": "qa-001",
  "skill_id": "qa_gate",
  "inputs": { "mode": "gate", "project_root": ".", "claude_root": ".claude", "scan_secrets": false }
}
```
2) Run:
`python .claude/tools/skills/skill_runner.py --in request_qa_gate.json`

## Acceptance
- `status=ok`
- No failures listed in `outputs.failures`

## If it fails
- Fix drift first (paths/contracts/topology) before any new work.
