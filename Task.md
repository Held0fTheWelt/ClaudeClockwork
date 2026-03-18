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
- .claude/docs/FIRST_STEPS.md

Goal:
Fix the registry description so it does not imply registry.md is the machine-readable canonical registry.

Required change:
- Preserve human-readable wording if useful
- Make the wording consistent with:
  .claude/skills/_index.json = machine-readable canonical output
  .claude/skills/registry.md = human-readable catalog

Do not:
- edit any other file
- broaden scope

Validation:
- show old line
- show new line

Report:
- Ollama agents used
- files changed
- exact before/after
- confirmation:
  - No Claude direct implementation
  - No Claude agents
  - No mixed execution