# Pure Ollama Agent Invocation

## How to Invoke Ollama Agents to Execute Tasks 8, 9, and Any New Task

This document shows how to invoke **pure Ollama agents** to execute tasks autonomously using the skill-forge pipeline. No human intervention, no Claude code generation.

---

## Quick Invocation: Execute All Tasks

```bash
#!/bin/bash
# Pure Ollama agent - execute tasks 8 and 9 autonomously

OLLAMA_MODEL="mistral"  # or any model: neural-chat, llama2, etc.
WORK_DIR="/mnt/d/ClaudeClockwork"

ollama run $OLLAMA_MODEL << 'OLLAMA_PROMPT'
You are an autonomous Ollama agent tasked with executing two jobs through the skill-forge pipeline.

**Your mission:** Execute both tasks and report results.

**Setup:**
- Work directory: /mnt/d/ClaudeClockwork
- You have access to shell commands

**Tasks:**

Task 8: Generate Documentation
  Command: cd /mnt/d/ClaudeClockwork && ./claudeclockwork/localai/agents/task_8_generate_documentation.sh
  Expected: Creates generated documentation artifacts through the forge pipeline

Task 9: Update CHANGELOG
  Command: cd /mnt/d/ClaudeClockwork && ./claudeclockwork/localai/agents/task_9_update_changelog.sh
  Expected: Creates CHANGELOG transformation code through the forge pipeline

**Instructions:**
1. Execute Task 8 and report exit code
2. Execute Task 9 and report exit code
3. For each task:
   - Check exit code (0 = success, non-zero = failure)
   - Extract task ID from .claude/forge_task*_result.json
   - Report archetype used
4. Provide final summary: did both tasks succeed?

**Execute now and report back with results.**
OLLAMA_PROMPT
```

---

## Master Orchestration via Ollama

```bash
ollama run mistral << 'PROMPT'
Execute this autonomous pipeline:

cd /mnt/d/ClaudeClockwork && ./claudeclockwork/localai/agents/run_all_tasks.sh

Report:
- Exit code
- Task 8 status and task ID
- Task 9 status and task ID
- Overall success/failure

Do not wait for human input. Execute autonomously.
PROMPT
```

---

## For Any New Task (Generic Approach)

When a **new task appears**, Ollama agents can execute it using the same pattern without modification:

```bash
ollama run mistral << 'PROMPT'
You are an autonomous Ollama agent. Execute a skill-forge pipeline task:

**Task:** [YOUR NEW TASK DESCRIPTION HERE]

**Execution:**
cd /mnt/d/ClaudeClockwork

# Use run_forge_task.sh with appropriate archetype:
# - reporter: Generate human-readable output (documentation, reports, guides)
# - transformer: Convert/transform data (update files, ETL operations)
# - scanner: Collect/scan data (find files, list items, inventory)
# - validator: Check/verify something (validate configs, verify state)
# - registry_helper: Manage skill registry (register new skills)

./claudeclockwork/localai/agents/run_forge_task.sh \
  [ARCHETYPE] \
  "[YOUR TASK DESCRIPTION]" \
  "[WRITE LOCATIONS or empty for read-only]" \
  "[OUTPUT_FILE.json]"

Report:
- Exit code (0 = success)
- Task ID from result JSON
- Generated artifacts
- Any errors if failed

Execute autonomously. No human input needed.
PROMPT
```

---

## Ollama Agent Python Helper

Create a Python script that Ollama agents can use:

```python
#!/usr/bin/env python3
# ollama_task_executor.py - Ollama agents execute tasks through forge pipeline

import subprocess
import json
import sys
from pathlib import Path

def run_forge_task(archetype, purpose, write_roots="", output_file="result.json"):
    """Execute a forge pipeline task via Ollama agent."""
    work_dir = Path("/mnt/d/ClaudeClockwork")

    result = subprocess.run([
        str(work_dir / "claudeclockwork/localai/agents/run_forge_task.sh"),
        archetype,
        purpose,
        write_roots,
        output_file
    ], cwd=str(work_dir), capture_output=True, text=True)

    return {
        "success": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_file": str(work_dir / ".claude" / output_file)
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ollama_task_executor.py <archetype> <purpose> [write_roots] [output_file]")
        sys.exit(1)

    archetype = sys.argv[1]
    purpose = sys.argv[2]
    write_roots = sys.argv[3] if len(sys.argv) > 3 else ""
    output_file = sys.argv[4] if len(sys.argv) > 4 else "result.json"

    result = run_forge_task(archetype, purpose, write_roots, output_file)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)
```

Usage from Ollama:
```bash
ollama run mistral << 'PROMPT'
Execute this task:
python3 /mnt/d/ClaudeClockwork/claudeclockwork/localai/agents/ollama_task_executor.py \
  reporter \
  "Generate comprehensive documentation" \
  "docs" \
  "forge_docs.json"

Report the exit code and task ID from the result.
PROMPT
```

---

## Ollama Agent Bash Script Helper

```bash
#!/bin/bash
# Generic task executor for Ollama agents

execute_task() {
    local archetype="$1"
    local purpose="$2"
    local write_roots="${3:-.}"
    local output_file="${4:-result.json}"

    cd /mnt/d/ClaudeClockwork

    ./claudeclockwork/localai/agents/run_forge_task.sh \
        "$archetype" \
        "$purpose" \
        "$write_roots" \
        "$output_file"

    return $?
}

# Example invocations by Ollama agents:
# execute_task reporter "Generate documentation" "docs" "doc_result.json"
# execute_task transformer "Update CHANGELOG" "." "changelog_result.json"
# execute_task scanner "Find Python files" "" "scan_result.json"
```

---

## Batch Execution by Ollama Agent

```bash
ollama run mistral << 'PROMPT'
Autonomous task batch execution:

# Task 8
echo "Executing Task 8..."
cd /mnt/d/ClaudeClockwork
./claudeclockwork/localai/agents/run_forge_task.sh reporter \
  "Generate comprehensive FORGE_PIPELINE.md documentation" docs task8.json
TASK8_EXIT=$?

# Task 9
echo "Executing Task 9..."
./claudeclockwork/localai/agents/run_forge_task.sh transformer \
  "Update CHANGELOG.md with feature summary" . task9.json
TASK9_EXIT=$?

# Report
echo "Task 8: $([ $TASK8_EXIT -eq 0 ] && echo 'PASS' || echo 'FAIL')"
echo "Task 9: $([ $TASK9_EXIT -eq 0 ] && echo 'PASS' || echo 'FAIL')"
[ $TASK8_EXIT -eq 0 ] && [ $TASK9_EXIT -eq 0 ] && echo "Overall: SUCCESS" || echo "Overall: FAILURE"

exit $(( $TASK8_EXIT + $TASK9_EXIT ))
PROMPT
```

---

## Key Principles for Ollama Agents

1. **Archetype Selection**: Choose based on task type
   - `reporter` → Generate human-readable output
   - `transformer` → Convert/transform data
   - `scanner` → Collect data
   - `validator` → Check/verify
   - `registry_helper` → Manage registry

2. **Write Roots**: Specify where agent can write
   - Empty `""` → Read-only
   - `"docs"` → Can write to docs/
   - `"."` → Can write to current directory

3. **Exit Code Interpretation**
   - `0` → Task succeeded
   - `1` → Task failed (check JSON result for details)

4. **Result JSON Location**
   - Results written to: `.claude/[output_file]`
   - Contains: task_id, archetype, generated code, validation results

---

## Safety Guarantees for Ollama Agents

✅ No forbidden patterns (shell=True, eval, exec)
✅ Network isolation enforced
✅ Write restrictions by allowed_write_roots
✅ Deterministic validation (6 gates)
✅ Smoke testing of generated code
✅ No LLM judgment in safety checks

Ollama agents can safely invoke these scripts with confidence that all safety constraints are enforced.

---

## Summary

**Pure Ollama agents can now:**
- Execute Tasks 8 and 9 autonomously
- Handle any new task using the same generic pattern
- Run multiple tasks in sequence
- Receive structured JSON results
- Know that all safety constraints are enforced

**No modification needed** to invoke new tasks - same scripts, same approach, any task.

