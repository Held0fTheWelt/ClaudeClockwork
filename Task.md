You are Claude running inside the ClaudeClockwork repository.

Execution contract:
This task must be executed by Ollama agents only.

Hard rules:
1. Use pure Ollama clients only.
2. You must delegate implementation work to Ollama agents.
3. You must not write or modify code yourself.
4. You must not use Claude agents.
5. You must not use mixed Claude+Ollama execution.
6. You must not bypass delegation by doing analysis-only and then applying edits yourself.
7. If Ollama execution is unavailable, blocked, or unhealthy, stop and report failure.
8. Do not fall back to Claude execution for any reason.
9. Do not return only a plan.
10. Do not broaden scope.

Required execution proof:
- Name the Ollama agent(s) used
- Show the exact Ollama-facing execution path/tooling used
- Show which files were modified by Ollama agent work
- State explicitly that Claude direct implementation was not used
- State explicitly that Claude agents were not used

Failure contract:
If you cannot complete this task through Ollama agents only, fail the task instead of implementing anything yourself.

Project language rule:
All project-facing changes must remain in English.

Mandatory enforcement:
- Treat any direct edit by Claude as a task failure.
- Treat any use of Claude agents as a task failure.
- Treat any mixed execution path as a task failure.
- Do not repair the task manually after an Ollama agent attempt.
- Do not compensate for agent failure by implementing the patch yourself.
- If needed, use Claude only to route, invoke, inspect, and report on Ollama agent work.

Role restriction:
Claude may orchestrate, dispatch, inspect results, and summarize and help fix broken skills.
Claude may not author implementation code, patches, manifests, docs, or tests for this task.
All implementation content must originate from Ollama agent execution.

You are Claude running inside the ClaudeClockwork repository.

Execution contract:
This task must be executed by Ollama agents only.

Hard rules:
1. Use pure Ollama clients only.
2. You must delegate implementation work to Ollama agents.
3. You must not write or modify code yourself.
4. You must not use Claude agents.
5. You must not use mixed Claude+Ollama execution.
6. You must not bypass delegation by doing analysis-only and then applying edits yourself.
7. If Ollama execution is unavailable, blocked, or unhealthy, stop and report failure.
8. Do not fall back to Claude execution for any reason.
9. Do not return only a plan.
10. Do not broaden scope.

Mandatory enforcement:
- Treat any direct edit by Claude as a task failure.
- Treat any use of Claude agents as a task failure.
- Treat any mixed execution path as a task failure.
- Do not repair the task manually after an Ollama agent attempt.
- Do not compensate for agent failure by implementing the patch yourself.
- If needed, use Claude only to route, invoke, inspect, and report on Ollama agent work.

You are Claude running inside the ClaudeClockwork repository.

Execution contract:
This task must be executed by Ollama agents only.

Hard rules:
1. Use pure Ollama clients only.
2. You must delegate implementation work to Ollama agents.
3. You must not write or modify code yourself.
4. You must not use Claude agents.
5. You must not use mixed Claude+Ollama execution.
6. You must not bypass delegation by doing analysis-only and then applying edits yourself.
7. If Ollama execution is unavailable, blocked, or unhealthy, stop and report failure.
8. Do not fall back to Claude execution for any reason.
9. Do not return only a plan.
10. Do not broaden scope.

Mandatory enforcement:
- Treat any direct edit by Claude as a task failure.
- Treat any use of Claude agents as a task failure.
- Treat any mixed execution path as a task failure.
- Do not repair the task manually after an Ollama agent attempt.
- Do not compensate for agent failure by implementing the patch yourself.
- If needed, use Claude only to route, invoke, inspect, and report on Ollama agent work.

This task must be executed by Ollama agents only.

Hard rules:
1. Use pure Ollama clients only.
2. You must delegate implementation work to Ollama agents.
3. You must not write or modify code yourself.
4. You must not use Claude agents.
5. You must not use mixed Claude+Ollama execution.
6. You must not bypass delegation by doing analysis-only and then applying edits yourself.
7. If Ollama execution is unavailable, blocked, or unhealthy, stop and report failure.
8. Do not fall back to Claude execution for any reason.
9. Do not return only a plan.
10. Do not broaden scope.

Mandatory enforcement:
- Treat any direct edit by Claude as a task failure.
- Treat any use of Claude agents as a task failure.
- Treat any mixed execution path as a task failure.
- Do not repair the task manually after an Ollama agent attempt.
- Do not compensate for agent failure by implementing the patch yourself.
- If needed, use Claude only to route, invoke, inspect, and report on Ollama agent work.

Task:
Implement only the smallest helper or guard needed to decide whether a model is forbidden for default mode.

Scope:
- claudeclockwork/localai/local_ollama_runtime.py
- or claudeclockwork/core/ollama/model_manager.py
- one file only if possible

Requirements:
1. Do not wire the guard into the full resolution path yet.
2. Implement only the minimum logic needed to answer:
   - allowed in default mode
   - forbidden in default mode
3. Keep names explicit and narrow.
4. No refactor.
5. No doc changes.

Validation:
- show one allowed example
- show one forbidden example
- show exact command/snippet
- show exact output

Report:
1. Ollama agents used
2. Files changed
3. Exact helper/guard added
4. Exact validation output
5. Confirmation:
   - No Claude direct implementation
   - No Claude agents
   - No mixed execution