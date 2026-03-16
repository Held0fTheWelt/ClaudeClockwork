# Task: Build Evidence Bundle

## Goal
Create a shareable evidence bundle (zip + manifest).

## Steps
1) Ensure an evidence run folder exists (recommended: run `evidence_init` first).
2) Create request `request_bundle.json`:
```json
{
  "type": "skill_request_spec",
  "request_id": "bundle-001",
  "skill_id": "evidence_bundle_build",
  "inputs": { "run_dir": "validation_runs/YYYY-MM-DD", "project_root": "." }
}
```
3) Run:
`python .claude/tools/skills/skill_runner.py --in request_bundle.json`

## Acceptance
- `artifacts/evidence_bundle_manifest.json` created
- `artifacts/evidence_bundle.zip` created
