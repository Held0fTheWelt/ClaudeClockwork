# Task: One-Button Release Cut

## Goal
Produce a deterministic **release evidence pack**:
- create evidence run dir
- run QA gate
- build evidence bundle
- (optional) redact
- write pack manifest

## Steps
1) Create request `request_release_cut.json`:
```json
{
  "type": "skill_request_spec",
  "request_id": "rel-001",
  "skill_id": "release_cut",
  "inputs": { "evidence_root": "validation_runs", "mode": "gate", "redact": true }
}
```
2) Run:
`python .claude/tools/skills/skill_runner.py --in request_release_cut.json`

## Acceptance
- `validation_runs/YYYY-MM-DD/reports/qa_gate.json` exists
- `validation_runs/YYYY-MM-DD/artifacts/evidence_bundle.zip` exists
- `validation_runs/YYYY-MM-DD/reports/pack_manifest.json` exists
