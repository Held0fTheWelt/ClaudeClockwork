# Skill Task: doc_write

Ziel: Dokumente **tool-first** schreiben, mit Diff und ohne Pfad-Traversal.

## Minimal Request

```json
{
  "type": "skill_request_spec",
  "request_id": "req-doc-001",
  "skill_id": "doc_write",
  "inputs": {
    "project_root": ".",
    "path": "Docs/Documentation/User_Guide.md",
    "content": "# User Guide\n\n(…)\n",
    "overwrite": true
  }
}
```

## Multi-file Request

```json
{
  "type": "skill_request_spec",
  "request_id": "req-doc-002",
  "skill_id": "doc_write",
  "inputs": {
    "project_root": ".",
    "overwrite": true,
    "files": [
      {"path": "Docs/Documentation/FAQ.md", "content": "# FAQ\n\n…\n"},
      {"path": "Docs/Tech/Architecture.md", "content": "# Architecture\n\n…\n"}
    ]
  }
}
```
