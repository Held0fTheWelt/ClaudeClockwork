# Skill Task: doc_review

Ziel: “Gegenlesen” tool-first starten: strukturelle Probleme finden, bevor man inhaltlich poliert.

## Review einzelner Datei

```json
{
  "type": "skill_request_spec",
  "request_id": "req-review-001",
  "skill_id": "doc_review",
  "inputs": {
    "project_root": ".",
    "scan_root": "Docs",
    "paths": ["Docs/Tutorials/01_Quickstart.md"]
  }
}
```

## Review ganzer Docs Tree

```json
{
  "type": "skill_request_spec",
  "request_id": "req-review-002",
  "skill_id": "doc_review",
  "inputs": {
    "project_root": ".",
    "scan_root": "Docs"
  }
}
```
