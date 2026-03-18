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
- Any direct implementation by Claude or any use of Claude agents invalidates the task result.

Failure rule:
A clear Ollama-agent failure report is required over any Claude-authored workaround.
Do not salvage the task with direct Claude edits.


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
9. Do not return only a plan.

Task:
Fix the current forbidden-model enforcement drift by removing mode-unaware blocking from model resolution and keeping mode-aware enforcement only at the actual call site.

Files to edit:
- claudeclockwork/core/ollama/model_manager.py
- claudeclockwork/core/agents/ollama_agent.py

Exact goal:
- model_manager.resolve_model(...) must become mode-agnostic again
- default-mode forbidden-model enforcement must remain active in OllamaAgent.__init__
- adaptive mode must not be blocked by default-mode enforcement during model resolution

Exact required changes:
1. In claudeclockwork/core/ollama/model_manager.py:
   - edit only OllamaModelManager.resolve_model
   - remove the three forbidden-model RuntimeError checks currently applied to:
     - per-invocation override
     - profile model
     - global default model
   - keep model resolution order unchanged
   - do not redesign the function

2. In claudeclockwork/core/agents/ollama_agent.py:
   - keep enforcement in OllamaAgent.__init__
   - replace the current direct check with the canonical helper:
     validate_model_not_forbidden
     from claudeclockwork.localai.local_ollama_runtime
   - apply it only when mode == "default"
   - keep the insertion point:
     after resolved, source = manager.resolve_model(...)
     before self.model = resolved

Non-goals:
- do not edit config files
- do not edit docs
- do not edit tests in this task
- do not refactor unrelated helpers
- do not change routing logic
- do not add new forbidden-model lists

Validation:
Run a direct Python smoke snippet that proves all three cases:
1. mode="default" + forbidden model -> raises RuntimeError
2. mode="adaptive" + same forbidden model -> does not fail at initialization because of default-mode enforcement
3. mode="default" + allowed model -> initializes successfully

Report format:
1. Ollama agents used
2. Files changed
3. Exact lines/functions changed
4. Exact validation snippet
5. Exact output
6. Confirmation:
   - No Claude direct implementation
   - No Claude agents
   - No mixed execution

Failure rule:
A clear Ollama-agent failure report is required over any Claude-authored workaround.
Do not salvage the task with direct Claude edits.