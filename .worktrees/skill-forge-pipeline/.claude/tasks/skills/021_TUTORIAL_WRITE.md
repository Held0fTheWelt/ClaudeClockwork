# Skill Task: tutorial_write

Ziel: Tutorials **spec-first** schreiben (oder Markdown persistieren) und dabei Pflichtsektionen prüfen.

## Tutorial aus Spec

```json
{
  "type": "skill_request_spec",
  "request_id": "req-tut-001",
  "skill_id": "tutorial_write",
  "inputs": {
    "project_root": ".",
    "path": "Docs/Tutorials/01_Quickstart.md",
    "overwrite": true,
    "tutorial_spec": {
      "title": "Quickstart",
      "audience": "End users",
      "goal": "Run the first workflow",
      "prerequisites": ["Python 3.11+"],
      "quickstart": ["Install dependencies", "Run the CLI"],
      "steps": [
        {"step": "Configure", "action": "Edit config file", "expected": "Config loads"}
      ],
      "verification": ["Confirm expected output"],
      "troubleshooting": ["If X happens, do Y"],
      "next_steps": ["Read the user guide"]
    }
  }
}
```

## Tutorial aus Markdown

```json
{
  "type": "skill_request_spec",
  "request_id": "req-tut-002",
  "skill_id": "tutorial_write",
  "inputs": {
    "project_root": ".",
    "path": "Docs/Tutorials/02_Advanced.md",
    "content": "# Advanced\n\n## Prerequisites\n- …\n\n## Quickstart\n1. …\n\n## Walkthrough\n1. …\n\n## Verification\n1. …\n\n## Troubleshooting\n- …\n\n## Next Steps\n- …\n",
    "overwrite": true
  }
}
```
