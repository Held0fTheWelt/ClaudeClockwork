# How to Add a New Skill

This guide describes the four-step process for adding a deterministic skill to the Clockwork framework.

## Overview

A skill is a deterministic, tool-first micro-workflow. Skills:
- Accept JSON input (stdin or first CLI argument)
- Produce JSON output (stdout)
- Use only Python stdlib (json, pathlib, glob, sys, os)
- Contain zero LLM calls
- Are invocable standalone or via skill_runner.py

---

## Step 1 — Write the JSON Schema

Create a schema file under `.claude/contracts/schemas/<skill_name>.schema.json`.

The schema documents the **input** shape. Document the output shape in `$defs.output`.

Minimal template:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MySkill",
  "description": "What this skill does.",
  "type": "object",
  "required": ["field_a"],
  "properties": {
    "field_a": { "type": "string", "description": "..." }
  },
  "additionalProperties": false,
  "$defs": {
    "output": {
      "type": "object",
      "required": ["result", "status"],
      "properties": {
        "result": { "type": "string" },
        "status": { "type": "string", "enum": ["ok", "fail"] }
      }
    }
  }
}
```

---

## Step 2 — Write an Example

Create `.claude/contracts/examples/<skill_name>_example.json`:

```json
{
  "input": { "field_a": "example value" },
  "expected_output": { "result": "expected result", "status": "ok" }
}
```

The example serves both as documentation and as a batch-validation fixture
(used by the `schema_batch_validate` skill).

---

## Step 3 — Write the Implementation

Create `.claude/tools/skills/<skill_name>.py`.

Rules:
- stdlib only (json, pathlib, glob, sys, os, hashlib, re, etc.)
- Must expose a `run(req: dict) -> dict` function for skill_runner
- Must expose a `main() -> int` standalone entrypoint
- Output dict must always include `"status": "ok" | "fail"`
- Never raise uncaught exceptions to the caller; catch and return `"status": "fail"`

Minimal template:

```python
#!/usr/bin/env python3
"""my_skill — one-line description."""
from __future__ import annotations
import json, sys

def _core_logic(field_a: str) -> dict:
    if not field_a:
        return {"result": "", "status": "fail", "error": "field_a is required"}
    return {"result": f"processed: {field_a}", "status": "ok"}

def run(req: dict) -> dict:
    inputs = req.get("inputs") or req.get("input") or {}
    result = _core_logic(inputs.get("field_a", ""))
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "my_skill",
        "status": result["status"],
        "outputs": result,
        "errors": [result["error"]] if result.get("error") else [],
        "warnings": [],
        "metrics": {},
    }

def main() -> int:
    raw = sys.argv[1] if len(sys.argv) >= 2 else sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON: {exc}\n")
        return 1
    if data.get("type") == "skill_request_spec":
        r = run(data)
        sys.stdout.write(json.dumps(r, indent=2) + "\n")
        return 0 if r["status"] == "ok" else 1
    result = _core_logic(data.get("field_a", ""))
    sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return 0 if result["status"] == "ok" else 1

if __name__ == "__main__":
    raise SystemExit(main())
```

---

## Step 4 — Add a Registry Entry

Open `.claude/skills/registry.md` and append an entry following the existing numbering:

```markdown
### N) my_skill
Brief description of what the skill does.
- Input: `{"field_a": "string"}`
- Output: `{"result": "string", "status": "ok"}`
- Standalone: `python tools/skills/my_skill.py '{"field_a": "value"}'`
```

Also add a row to the MVP02 table at the bottom of the registry:

```markdown
| my_skill | Brief description | contracts/schemas/my_skill.schema.json | tools/skills/my_skill.py |
```

---

## Verification checklist

- [ ] Schema file exists at `.claude/contracts/schemas/<skill_name>.schema.json`
- [ ] Example file exists at `.claude/contracts/examples/<skill_name>_example.json`
- [ ] Implementation exists at `.claude/tools/skills/<skill_name>.py`
- [ ] Registry entry added in `.claude/skills/registry.md`
- [ ] Standalone invocation works: `python .claude/tools/skills/<skill_name>.py '<json>'`
- [ ] Output is valid JSON with `"status": "ok"` on success

---

## Reference: MVP02 example skills

| Skill | Standalone test |
|-------|----------------|
| hello | `python .claude/tools/skills/hello.py '{"name": "World"}'` |
| scan  | `python .claude/tools/skills/scan.py '{"path": ".", "pattern": "**/*.py"}'` |
| report | `python .claude/tools/skills/report.py '{"title": "T", "items": ["a"]}'` |
