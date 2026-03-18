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
- .claude/tools/boot_check.py

Goal:
Make boot_check validate manifest agent_type values against the canonical mode vocabulary used by the core mode system.

Required change:
1. Find the current valid agent_type set used by boot_check manifest validation.
2. Replace it so the allowed values are exactly:
   - local
   - ollama
   - claude
   - hybrid
3. Remove legacy acceptance of values such as:
   - mixed
   - external
4. Keep the rest of boot_check behavior unchanged unless a tiny adjacent update is required for consistency.

Non-goals:
- do not edit manifests
- do not edit any other file
- do not redesign boot_check
- do not add new policy logic beyond the valid set correction

Validation:
1. Print the old valid_types line or block.
2. Print the new valid_types line or block.
3. Run:
   python3 .claude/tools/boot_check.py
4. Show the exact output.

Expected outcome:
- If invalid manifest agent_type values still exist in the repo, boot_check should now fail instead of passing.
- If all manifests are already canonical, boot_check may pass. In that case, report that clearly.