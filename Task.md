You are Claude running inside the ClaudeClockwork repository.

This is an Ollama-only implementation task.
Any direct implementation by Claude or any use of Claude agents invalidates the task result.

Execution contract:
1. Use pure Ollama clients only.
2. Delegate all implementation work to Ollama agents.
3. Do not write or modify code yourself.
4. Do not use Claude agents.
5. Do not use mixed Claude+Ollama execution.
6. Do not bypass delegation by analyzing and then applying edits yourself.
7. If Ollama execution is unavailable, blocked, or unhealthy, fail the task.
8. Do not broaden scope.
9. If the scoped target is already compliant, do a no-op and report proof.

Report format:
1. Ollama agents used
2. Files changed
3. Exact validation command or snippet
4. Exact output
5. Confirmation:
   - No Claude direct implementation
   - No Claude agents
   - No mixed execution

Task:
Edit exactly one file:
- .claude/python/README.md

Goal:
Make the pointer text consistent with the current registry split.

Required change:
1. Keep the file as a deprecated pointer
2. Replace the current “Skills registry” wording so it no longer implies registry.md is the sole canonical registry
3. Clarify:
   - skills/_index.json = machine-readable canonical registry output
   - skills/registry.md = human-readable catalog

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