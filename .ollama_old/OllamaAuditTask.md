You are working on a local ClaudeClockwork + Ollama recovery and stabilization task.

Mission:
Diagnose, recover, stabilize, and document the local Ollama runtime so ClaudeClockwork can use it reliably again.

Known symptoms:
- /api/generate returns a mix of 200 / 499 / 500
- some model loads take many minutes
- some Ollama model processes consume very high CPU and large RAM
- problematic runs appear CPU-only
- problematic runs show UseMmap:false
- multiple heavy runners may be loaded at the same time
- models are located on /mnt/e/...
- current local multi-agent behavior appears to overload the inference layer

Important constraints:
- Do not reinstall everything unless clearly necessary
- Do not delete models unless clearly necessary
- Do not download large new models unless clearly justified
- Do not run multiple heavy model tasks in parallel
- Prefer a stable local operating mode over maximum concurrency
- Preserve the current setup as much as possible while making it reliable
- Be explicit about what you changed and why

Execution plan:

Phase 1 — Assess current state
- Inspect running ollama processes
- Inspect CPU/RAM pressure
- Test whether ollama serve is responsive
- Call /api/tags
- Collect recent Ollama logs
- Determine whether current/problematic runs are CPU-only
- Determine whether mmap is disabled
- Determine whether multiple runners are active
- Produce a short diagnosis summary

Phase 2 — Clean recovery
- Stop hung generate workloads
- Stop stale or orphaned runners
- Cleanly restart ollama serve
- Re-test /api/tags
- Confirm the service is healthy before continuing

Phase 3 — Verify GPU and mmap path
- Inspect service startup mode, environment variables, wrappers, and scripts
- Determine why some runs had GPU offload while later runs had GPULayers:[]
- Determine why UseMmap:false is active
- Check whether the current WSL/service setup needs correction
- If needed, patch the relevant startup/config scripts conservatively

Phase 4 — Establish a safe local ClaudeClockwork mode
- Define a single-heavy-model local mode
- Ensure heavy tasks are serialized
- Ensure small/medium models are used for docs/summary/plan tasks
- Reserve heavy models for code/judge/integration only
- Prevent unnecessary parallel heavy runner launches
- If needed, update local setup/config files to reflect this mode

Phase 5 — Validate with real tests
Run this exact sequence:
1. /api/tags
2. short generate using a small/medium model
3. short generate using the main heavy model
4. one ClaudeClockwork run with only one heavy task
5. repeat once to verify stability over a second pass

For each test, record:
- success/failure
- latency
- whether GPU offload is active
- whether mmap is active
- whether extra runners appear
- whether 499/500 errors occur

Phase 6 — Final report
Deliver:
- root cause summary
- exact changes made
- exact files changed
- stable local operating rules for ClaudeClockwork
- unresolved risks
- recommended next steps

Output requirements:
- Be concise but specific
- Prefer facts from logs/process state over guesses
- Do not just say “it is slow”; explain why
- If you modify files, show a minimal diff summary
- Do not leave the system in a partially broken state
- If something cannot be fully fixed, leave it in the safest stable mode you can achieve