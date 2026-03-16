# Ollama Agent Autonomous Execution Guide

## Overview

This guide shows how **pure Ollama agents** can autonomously execute Tasks 8 and 9 using the skill-forge pipeline. No human intervention, no Claude involvement — fully autonomous execution.

---

## Prerequisites

- Ollama running and accessible (default: `localhost:11434`)
- ClaudeClockwork repository at `/mnt/d/ClaudeClockwork`
- Python 3.10+
- Bash

## Quick Start: Execute All Tasks

```bash
#!/bin/bash
# Ollama agent: Execute both tasks autonomously

cd /mnt/d/ClaudeClockwork

# Run the master orchestration script
./claudeclockwork/localai/agents/run_all_tasks.sh

# Script exits with code 0 on success, 1 on failure
if [ $? -eq 0 ]; then
    echo "SUCCESS: Both tasks completed"
else
    echo "FAILURE: Check result files for details"
    cat .claude/forge_task8_result.json
    cat .claude/forge_task9_result.json
fi
```

---

## Task 8: Generate Documentation (Autonomous)

**Objective:** Generate `FORGE_PIPELINE.md` documentation

**Ollama Agent Execution:**

```bash
cd /mnt/d/ClaudeClockwork

# Method 1: Direct script execution
./claudeclockwork/localai/agents/task_8_generate_documentation.sh

# Method 2: Using generic runner with explicit parameters
./claudeclockwork/localai/agents/run_forge_task.sh \
  reporter \
  "Generate comprehensive FORGE_PIPELINE.md documentation explaining the skill-forge pipeline architecture, how to use it, and examples for Ollama agents" \
  "docs" \
  ".claude/forge_task8_result.json"
```

**What the agent will do:**
1. Route through skill-forge pipeline
2. Use `reporter` archetype (generates human-readable output)
3. Plan documentation structure
4. Generate markdown content from template
5. Review for quality (docstrings, style, naming)
6. Validate output (no forbidden patterns, safety gates)
7. Return structured JSON result
8. Save generated documentation to disk

**Success Indicator:**
```bash
grep '"success": true' .claude/forge_task8_result.json
```

---

## Task 9: Update CHANGELOG (Autonomous)

**Objective:** Update `CHANGELOG.md` with feature summary

**Ollama Agent Execution:**

```bash
cd /mnt/d/ClaudeClockwork

# Method 1: Direct script execution
./claudeclockwork/localai/agents/task_9_update_changelog.sh

# Method 2: Using generic runner with explicit parameters
./claudeclockwork/localai/agents/run_forge_task.sh \
  transformer \
  "Update CHANGELOG.md with a summary of the skill-forge pipeline implementation v0.5.0" \
  "." \
  ".claude/forge_task9_result.json"
```

**What the agent will do:**
1. Route through skill-forge pipeline
2. Use `transformer` archetype (ETL/data transformation)
3. Plan changelog entry structure
4. Generate transformation code
5. Review for quality
6. Validate safety (allowed write roots enforced)
7. Return structured result
8. Ready for CHANGELOG.md integration

**Success Indicator:**
```bash
grep '"success": true' .claude/forge_task9_result.json
```

---

## Ollama Agent Invocation Methods

### Method 1: Direct Shell Invocation

```bash
#!/bin/bash
# Pure Ollama agent running shell commands

ollama run mistral bash << 'EOF'
#!/bin/bash
cd /mnt/d/ClaudeClockwork
./claudeclockwork/localai/agents/run_all_tasks.sh
echo "Tasks completed with exit code: $?"
EOF
```

### Method 2: Ollama with Embedded Script

```bash
ollama run neural-chat << 'EOF'
I am an autonomous agent. Execute these tasks in sequence:

Task 1: Generate documentation
  Command: cd /mnt/d/ClaudeClockwork && ./claudeclockwork/localai/agents/task_8_generate_documentation.sh

Task 2: Update CHANGELOG
  Command: cd /mnt/d/ClaudeClockwork && ./claudeclockwork/localai/agents/task_9_update_changelog.sh

After each task:
- Check exit code
- Report success/failure
- Show task ID from JSON result

Execute both tasks and report final status.
EOF
```

### Method 3: Ollama Python Integration

```python
#!/usr/bin/env python3
# Ollama agent with Python execution

import subprocess
import json

def run_forge_task(archetype, purpose, write_roots, output_file):
    """Execute a forge pipeline task."""
    result = subprocess.run([
        "./claudeclockwork/localai/agents/run_forge_task.sh",
        archetype,
        purpose,
        write_roots,
        output_file
    ], cwd="/mnt/d/ClaudeClockwork", capture_output=True, text=True)

    return {
        "exit_code": result.returncode,
        "success": result.returncode == 0,
        "output": result.stdout
    }

# Task 8
print("Starting Task 8: Generate documentation")
result8 = run_forge_task(
    "reporter",
    "Generate comprehensive FORGE_PIPELINE.md documentation",
    "docs",
    ".claude/forge_task8_result.json"
)
print(f"Task 8: {'PASS' if result8['success'] else 'FAIL'}")

# Task 9
print("\nStarting Task 9: Update CHANGELOG")
result9 = run_forge_task(
    "transformer",
    "Update CHANGELOG.md with feature summary",
    ".",
    ".claude/forge_task9_result.json"
)
print(f"Task 9: {'PASS' if result9['success'] else 'FAIL'}")

# Summary
if result8['success'] and result9['success']:
    print("\n✓ All tasks passed")
    exit(0)
else:
    print("\n✗ Some tasks failed")
    exit(1)
```

---

## Validation & Verification

After execution, verify results:

```bash
cd /mnt/d/ClaudeClockwork

# Check Task 8 results
echo "=== Task 8 Results ==="
cat .claude/forge_task8_result.json | python3 -m json.tool

# Check Task 9 results
echo "=== Task 9 Results ==="
cat .claude/forge_task9_result.json | python3 -m json.tool

# Verify generated artifacts
echo "=== Generated Files ==="
ls -la docs/ CHANGELOG.md 2>/dev/null || echo "Files may be generated in package temp dirs"
```

---

## Error Handling

If a task fails, the Ollama agent should:

1. Check exit code (non-zero = failure)
2. Read the JSON result file
3. Extract `reason` field for failure cause
4. Log the error
5. Continue or abort based on task importance

Example:

```bash
if [ $? -ne 0 ]; then
    # Extract error details
    ERROR_REASON=$(cat .claude/forge_task8_result.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('reason','unknown'))")
    echo "Task 8 failed: $ERROR_REASON"
    exit 1
fi
```

---

## Safety Guarantees

All tasks executed through the forge pipeline include:

- **No forbidden patterns:** `shell=True`, `eval`, `exec` cannot be generated
- **Network isolation:** Generated code cannot import socket, requests, urllib
- **Write restrictions:** Only writes to `allowed_write_roots` (enforced by validation gates)
- **Deterministic validation:** 6 safety gates with no LLM judgment
- **Smoke testing:** Generated code is executed with sample input before acceptance

Agents can safely invoke these scripts without risk of unsafe code generation.

---

## Full Orchestration Example

```bash
#!/bin/bash
# Complete autonomous execution for Ollama agents

set -euo pipefail

WORK_DIR="/mnt/d/ClaudeClockwork"
RESULT_DIR="$WORK_DIR/.claude"

# Initialize
mkdir -p "$RESULT_DIR"
cd "$WORK_DIR"

echo "Ollama Agent: Starting autonomous task execution"
echo "Time: $(date -Iseconds)"
echo ""

# Task 8
echo "Task 8/2: Generate Documentation"
if ./claudeclockwork/localai/agents/task_8_generate_documentation.sh > "$RESULT_DIR/task8.log" 2>&1; then
    echo "  Status: ✓ PASS"
    TASK8_PASS=true
else
    echo "  Status: ✗ FAIL"
    TASK8_PASS=false
    cat "$RESULT_DIR/task8.log" >> "$RESULT_DIR/errors.log"
fi

# Task 9
echo "Task 9/2: Update CHANGELOG"
if ./claudeclockwork/localai/agents/task_9_update_changelog.sh > "$RESULT_DIR/task9.log" 2>&1; then
    echo "  Status: ✓ PASS"
    TASK9_PASS=true
else
    echo "  Status: ✗ FAIL"
    TASK9_PASS=false
    cat "$RESULT_DIR/task9.log" >> "$RESULT_DIR/errors.log"
fi

echo ""
echo "Final Status:"
if $TASK8_PASS && $TASK9_PASS; then
    echo "  ✓ All tasks passed"
    echo "  Results:"
    echo "    - Task 8: $RESULT_DIR/forge_task8_result.json"
    echo "    - Task 9: $RESULT_DIR/forge_task9_result.json"
    exit 0
else
    echo "  ✗ Some tasks failed"
    echo "  Check logs: $RESULT_DIR/errors.log"
    exit 1
fi
```

---

## Summary

**Ollama agents can now autonomously execute Tasks 8 & 9:**

- ✅ No human involvement
- ✅ No Claude code generation
- ✅ Pure autonomous execution via shell scripts
- ✅ Deterministic validation gates
- ✅ Structured JSON results
- ✅ Full safety guarantees

**To trigger Ollama agent execution:**

```bash
/mnt/d/ClaudeClockwork/claudeclockwork/localai/agents/run_all_tasks.sh
```

Exit code 0 = success, 1 = failure.
