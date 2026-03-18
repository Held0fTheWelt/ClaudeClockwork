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


Any Claude-written patch or any Claude-agent use fails the task.

Rules:
- Use pure Ollama clients only
- Delegate all implementation work to Ollama agents
- Do not write or modify code yourself
- Do not use Claude agents
- Do not use mixed execution
- If Ollama is unavailable or unhealthy, fail
- Do not broaden scope

Task:
Edit exactly one file:
- .claude/skills/demo/hello/manifest.json

Goal:
Correct the manifest agent_type based on the actual execution path.

Required change:
1. Inspect .claude/skills/demo/hello/skill.py
2. Inspect the legacy tool path it invokes
3. Set metadata.mode_requirements.agent_type to the single correct canonical value
4. Do not change any other field unless absolutely required for consistency

Expected result:
- agent_type should reflect a local deterministic execution path, not a Claude LLM path

Validation:
- show before/after for metadata.mode_requirements
- briefly state why the chosen value matches the implementation path

Report:
- Ollama agents used
- files changed
- exact before/after
- exact reasoning
- confirmation:
  - No Claude direct implementation
  - No Claude agents
  - No mixed execution