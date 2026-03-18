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
- .claude/MODEL_POLICY.md

Goal:
Fix the broken pointer so it no longer points to a missing root file.

Required change:
- Remove the pointer to:
  ../MODEL_POLICY.md
- Replace it with pointer text that references real files inside .claude only
- Keep the file as a pointer, not a full policy rewrite

Do not:
- edit any other file
- rewrite policy content broadly

Validation:
- show old pointer line
- show new pointer line
- prove each referenced target exists

Report:
- Ollama agents used
- files changed
- exact output
- confirmation:
  - No Claude direct implementation
  - No Claude agents
  - No mixed execution