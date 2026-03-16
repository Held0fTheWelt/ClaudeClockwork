# Autonomous Agent Guide: Forge Pipeline

This guide explains how **Ollama agents** (or any autonomous system) can execute tasks through the skill-forge pipeline without human intervention.

---

## Quick Start for Ollama Agents

### Generic Task Execution Script

**Location:** `claudeclockwork/localai/agents/run_forge_task.sh`

**Purpose:** Reusable entry point for ANY Ollama agent to execute ANY task through the forge pipeline.

### Usage

```bash
./run_forge_task.sh <archetype> <purpose> [allowed_write_roots] [output_file]
```

### Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `archetype` | Yes | Task type (see Archetypes below) | `reporter` |
| `purpose` | Yes | Task description/goal | `"Generate FORGE_PIPELINE.md documentation"` |
| `allowed_write_roots` | No | Paths where task can write (comma-separated) | `"claudeclockwork/docs"` |
| `output_file` | No | Where to save results (JSON) | `"result.json"` |

---

## Archetypes

Each archetype maps to a problem type. Choose the one that fits your task:

| Archetype | Use When | Example Task |
|-----------|----------|--------------|
| **scanner** | You need to collect/scan data | "Find all Python files in a directory" |
| **validator** | You need to check/verify something | "Validate JSON config files" |
| **reporter** | You need to generate human-readable output | "Create documentation" |
| **transformer** | You need to convert/transform data | "Update CHANGELOG.md with new features" |
| **registry_helper** | You need to manage the skill registry | "Register a new skill" |

---

## Examples for Ollama Agents

### Example 1: Generate Documentation (Task 8)

```bash
./run_forge_task.sh \
  reporter \
  "Generate comprehensive user guide for the skill-forge pipeline" \
  "claudeclockwork/docs" \
  "FORGE_PIPELINE.md"
```

**What happens:**
1. Forge pipeline plans the documentation structure
2. Generates markdown content from reporter template
3. Reviews for quality (docstrings, style, naming)
4. Validates output (syntax, safety gates)
5. Writes result to `FORGE_PIPELINE.md`
6. Saves execution details to JSON output

### Example 2: Update CHANGELOG (Task 9)

```bash
./run_forge_task.sh \
  transformer \
  "Update CHANGELOG.md with feature summary for skill-forge v0.5.0" \
  "." \
  "CHANGELOG_update.json"
```

**What happens:**
1. Plans transformation structure
2. Generates changelog entry code
3. Reviews for quality
4. Validates transformation safety
5. Saves result for manual integration or further processing

### Example 3: Create a Validator Skill

```bash
./run_forge_task.sh \
  validator \
  "Create a skill that validates YAML configuration files" \
  "" \
  "validator_result.json"
```

**What happens:**
- Read-only task (no `allowed_write_roots`)
- Generates validator code
- Returns Python skill code in result

---

## How Ollama Agents Use This

### From Bash/Shell

```bash
#!/bin/bash
# Ollama agent execution script

cd /path/to/ClaudeClockwork/.worktrees/skill-forge-pipeline

# Execute any task
./run_forge_task.sh reporter "Your task description" "output_dir" "result.json"

# Check if successful
if [ $? -eq 0 ]; then
    echo "Task completed successfully"
    cat result.json | jq '.result'
else
    echo "Task failed"
    exit 1
fi
```

### From Python (Ollama running Python code)

```python
import subprocess
import json

# Execute forge task
result = subprocess.run([
    "./run_forge_task.sh",
    "reporter",
    "Generate documentation",
    "docs",
    "result.json"
], cwd="/path/to/skill-forge-pipeline", capture_output=True, text=True)

if result.returncode == 0:
    with open("result.json") as f:
        output = json.load(f)
    print(output["result"])
else:
    print(f"Error: {result.stderr}")
```

### From Ollama Direct Invocation

```bash
# Pass the execution as a prompt to Ollama
ollama run <model> < <(cat <<'EOF'
Execute this task autonomously using the forge pipeline:

Task: Generate documentation for the skill-forge pipeline
Archetype: reporter
Purpose: Create FORGE_PIPELINE.md user guide
Write location: claudeclockwork/docs

Use this command:
./run_forge_task.sh reporter "Generate comprehensive user guide for the skill-forge pipeline" "claudeclockwork/docs" "FORGE_PIPELINE.md"

Then:
1. Run the command
2. Check the JSON output
3. Verify the generated documentation is present
4. Report success/failure and any artifacts generated
EOF
)"
```

---

## Understanding the Output

### Successful Execution

```json
{
  "success": true,
  "task_id": "forge_20260316_143022_1710604822",
  "archetype": "reporter",
  "result": {
    "success": true,
    "forge_result": {
      "task_id": "...",
      "archetype": "reporter",
      "code": {
        "__init__.py": "...",
        "main.py": "...",
        "schema.py": "..."
      },
      "manifest": { ... },
      "package_root": "/tmp/xyz/forge_xyz"
    },
    "validation": {
      "passed": true,
      "checks": { ... },
      "timestamp": "..."
    }
  },
  "timestamp": "2026-03-16T14:30:22.123456"
}
```

### Failed Execution

```json
{
  "success": false,
  "task_id": "forge_20260316_143022_1710604822",
  "archetype": "reporter",
  "result": {
    "success": false,
    "reason": "review_failed",
    "issues": [
      {"file": "main.py", "line": 15, "severity": "warning", "message": "..."}
    ]
  },
  "timestamp": "2026-03-16T14:30:22.123456"
}
```

---

## Key Points for Agents

1. **No Human Intervention Needed** - Script handles everything autonomously
2. **Generic & Reusable** - Same script works for any archetype, any task
3. **Safety Built-in** - Validation gates prevent unsafe code
4. **Structured Output** - JSON results for programmatic processing
5. **Status Codes** - Exit 0 = success, exit 1 = failure

---

## Architecture: How It Works

```
Ollama Agent
    ↓
run_forge_task.sh (entry point)
    ↓
generic_forge_agent.py (task launcher)
    ↓
SkillForgeRunner (orchestrator)
    ↓
code.plan → code.forge → code.review → code.validate
    ↓
Structured Result (JSON)
```

---

## Safety & Constraints

All tasks executed through this script include:

- **Forbidden patterns:** `shell=True`, `eval`, `exec` (cannot be circumvented)
- **Network isolation:** No socket, requests, urllib imports
- **Write restrictions:** Enforced via `allowed_write_roots`
- **Deterministic validation:** No LLM judgment in safety gates
- **Smoke testing:** Generated code is executed with sample input

---

## For Multiple Sequential Tasks

```bash
#!/bin/bash
# Execute multiple tasks in sequence

WORKDIR="/mnt/d/ClaudeClockwork/.worktrees/skill-forge-pipeline"
cd "$WORKDIR"

echo "Task 8: Generate documentation"
./run_forge_task.sh reporter "Generate FORGE_PIPELINE.md" "docs" "task8.json"
if [ $? -ne 0 ]; then echo "Task 8 failed"; exit 1; fi

echo "Task 9: Update CHANGELOG"
./run_forge_task.sh transformer "Update CHANGELOG.md" "." "task9.json"
if [ $? -ne 0 ]; then echo "Task 9 failed"; exit 1; fi

echo "All tasks completed"
```

---

## Summary

This script enables **full autonomous execution** of ANY forge pipeline task by Ollama agents:

- ✅ Generic (works for any task)
- ✅ Reusable (no modification needed)
- ✅ Safe (deterministic validation gates)
- ✅ Structured output (JSON results)
- ✅ No human intervention required

**Ollama agents can now autonomously generate code, documentation, and artifacts through the skill-forge pipeline.**
