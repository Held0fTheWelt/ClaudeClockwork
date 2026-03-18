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
- .claude/docs/DOC_SKILLS.md

Goal:
Fix the “full skill registry” wording so it does not treat registry.md as the machine-readable canonical registry.

Required change:
- Keep registry.md as human-readable catalog if needed
- Align wording with _index.json as machine-readable canonical registry output

Do not:
- edit any other file
- rewrite the document broadly

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