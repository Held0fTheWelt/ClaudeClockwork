# Skills Quickstart

## Run a skill
Example (repo validate):
1) Create a request JSON:
```json
{
  "type": "skill_request_spec",
  "request_id": "req-001",
  "skill_id": "repo_validate",
  "inputs": { "root": ".", "scan_secrets": false }
}
```
2) Run:
`python tools/skills/skill_runner.py --in request.json`

## When to use skills
- Any time you want deterministic checks, evidence folders, schema validation, hashing, or spend regression checks.

## Run the hard QA gate
```json
{
  "type": "skill_request_spec",
  "request_id": "req-qa-001",
  "skill_id": "qa_gate",
  "inputs": { "mode": "gate", "project_root": ".", "claude_root": ".claude" }
}
```
Run:
`python tools/skills/skill_runner.py --in request_qa.json`

## One-button release cut (evidence + gate + bundle)
```json
{
  "type": "skill_request_spec",
  "request_id": "req-rel-001",
  "skill_id": "release_cut",
  "inputs": { "evidence_root": "validation_runs", "mode": "gate", "redact": true }
}
```
Run:
`python tools/skills/skill_runner.py --in request_release.json`

## Write a documentation file (doc_write)
```json
{
  "type": "skill_request_spec",
  "request_id": "req-doc-001",
  "skill_id": "doc_write",
  "inputs": {
    "project_root": ".",
    "path": "Docs/Documentation/User_Guide.md",
    "content": "# User Guide\n\n(…)",
    "overwrite": true
  }
}
```

## Write a tutorial from a structured spec (tutorial_write)
```json
{
  "type": "skill_request_spec",
  "request_id": "req-tut-001",
  "skill_id": "tutorial_write",
  "inputs": {
    "project_root": ".",
    "path": "Docs/Tutorials/01_Quickstart.md",
    "tutorial_spec": {
      "title": "Quickstart",
      "audience": "End users",
      "goal": "Run the first workflow",
      "prerequisites": ["Python 3.11+"],
      "quickstart": ["Install dependencies", "Run the CLI"],
      "steps": [{"step": "Configure", "action": "Edit config", "expected": "Config loads"}],
      "verification": ["Confirm expected output"],
      "troubleshooting": ["If X happens, do Y"],
      "next_steps": ["Read the user guide"]
    },
    "overwrite": true
  }
}
```

## Lint-review docs (doc_review)
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

## Compare two repos/folders (repo_compare)
```json
{
  "type": "skill_request_spec",
  "request_id": "req-compare-001",
  "skill_id": "repo_compare",
  "inputs": {
    "project_root": ".",
    "left_root": "../ClaudeCode",
    "right_root": "../LlamaCode",
    "exclude_prefixes": [".git/", "__pycache__/"],
    "write_report": true
  }
}
```

## Write a screencast script (screencast_script)
```json
{
  "type": "skill_request_spec",
  "request_id": "req-video-001",
  "skill_id": "screencast_script",
  "inputs": {
    "project_root": ".",
    "path": "Docs/Documentation/Screencast_Quickstart.md",
    "script_spec": {
      "title": "Quickstart Screencast",
      "audience": "End users",
      "goal": "Show installation + first run",
      "duration": "5-7 min",
      "chapters": [
        {"timestamp": "00:00", "title": "Intro", "on_screen": "Open repo", "narration": "What we will do"},
        {"timestamp": "01:00", "title": "Install", "on_screen": "Run install command", "narration": "Explain prerequisites"}
      ]
    },
    "overwrite": true
  }
}
```
