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

Failure rule:
A clear Ollama-agent failure report is required over any Claude-authored workaround.
Do not salvage the task with direct Claude edits.

Task:
Add a minimal regression suite covering only the repaired drift points.

Scope:
- a small tests directory if needed
- no network dependency
- no broad integration matrix

Required tests:
1. boot_check catches invalid agent_type
2. the three former mixed manifests now use canonical values
3. MODEL_POLICY pointer target exists
4. canonical machine-readable skill registry path is asserted
5. forbidden-model enforcement proof matches the repaired behavior

Validation:
- run only the targeted tests
- show exact command
- show exact result

Report:
1. Ollama agents used
2. Files changed
3. Exact validation command
4. Exact result
5. Confirmation:
   - No Claude direct implementation
   - No Claude agents
   - No mixed execution