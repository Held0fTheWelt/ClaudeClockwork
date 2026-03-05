# Task: Redact Evidence (Security/Privacy)

## Goal
Create a redacted copy of an evidence folder for sharing.

## Steps
1) Create request `request_redact.json`:
```json
{
  "type": "skill_request_spec",
  "request_id": "redact-001",
  "skill_id": "security_redactor",
  "inputs": { "input_dir": "validation_runs/YYYY-MM-DD", "output_dir": "validation_runs/YYYY-MM-DD_redacted" }
}
```
2) Run:
`python .claude/tools/skills/skill_runner.py --in request_redact.json`

## Acceptance
- Redacted folder created
- `reports/redaction_report.json` exists in the redacted folder
