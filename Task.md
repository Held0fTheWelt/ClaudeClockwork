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
- .claude/tools/boot_check.py

Goal:
Update the manifest mode validation to use the canonical agent_type values.

Required change:
- Replace the current valid_types set
- Old values include mixed and external
- New allowed values must be exactly:
  local
  ollama
  claude
  hybrid

Do not:
- edit any manifest
- edit any other file
- refactor boot_check broadly

Validation:
- show the old valid_types line
- show the new valid_types line
- run:
  python3 .claude/tools/boot_check.py
- show exact output

Report:
- Ollama agents used
- files changed
- exact output
- confirmation:
  - No Claude direct implementation
  - No Claude agents
  - No mixed execution