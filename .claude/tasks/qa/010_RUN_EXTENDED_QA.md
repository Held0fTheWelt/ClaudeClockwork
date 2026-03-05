# Task: Run Extended QA

## Goal
Run heavier QA checks before a release cut.

## Steps
1) Schema batch validation:
```json
{
  "type": "skill_request_spec",
  "request_id": "qa-ext-001",
  "skill_id": "schema_batch_validate",
  "inputs": { "claude_root": ".claude" }
}
```
Run:
`python .claude/tools/skills/skill_runner.py --in request_schema_batch.json`

2) Capability snapshot:
Use `tasks/ops/120_BUILD_CAPABILITY_MAP.md`.

3) If sharing evidence:
Use `tasks/security/000_REDACT_EVIDENCE.md`.

## Acceptance
- `schema_batch_validate` returns `status=ok`.
