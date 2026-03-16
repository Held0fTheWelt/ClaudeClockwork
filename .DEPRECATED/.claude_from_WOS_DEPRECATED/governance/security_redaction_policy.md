# Security & Privacy Redaction Policy (v17.6)

## Rule
Before sharing logs/evidence outside your local environment:
- run `security_redactor`
- share only the redacted directory + `reports/redaction_report.json`

## Why
Evidence can contain:
- API keys / tokens
- private key blocks
- local paths

## Allowed output
- redacted evidence directory
- manifest + pack manifest
