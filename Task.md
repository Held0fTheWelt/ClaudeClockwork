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
- .claude/INDEX.md

Goal:
Fix the MODEL_POLICY entry so it no longer claims a canonical root MODEL_POLICY.md file.

Required change:
- Find the line that says MODEL_POLICY.md points to root MODEL_POLICY.md
- Replace it with wording that matches the real .claude-local pointer/canonical structure

Do not:
- edit any other file
- rewrite the full index

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