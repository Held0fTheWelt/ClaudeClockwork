You are Claude running inside the ClaudeClockwork repository.

Ollama-only task.
Any Claude-written patch or any Claude-agent use fails the task.

Rules:
- Use pure Ollama clients only
- Delegate all implementation work to Ollama agents
- Do not write or modify code yourself
- Do not use Claude agents
- Do not use mixed execution
- If Ollama is unavailable or unhealthy, fail
- Do not broaden scope
- If the file is already compliant, do a no-op and report proof

Task:
Edit exactly one file:
- .claude/knowledge/index.md

Goal:
Fix the table entry that currently presents .claude/skills/registry.md as the skill registry without clarifying its human-readable role.

Required change:
- Clarify:
  .claude/skills/_index.json = machine-readable canonical registry output
  .claude/skills/registry.md = human-readable catalog

Do not:
- edit any other file
- rewrite the knowledge index broadly

Validation:
- show old table row
- show new table row

Report:
- Ollama agents used
- files changed
- exact before/after
- confirmation:
  - No Claude direct implementation
  - No Claude agents
  - No mixed execution