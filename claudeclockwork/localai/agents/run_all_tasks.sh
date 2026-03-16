#!/bin/bash
# Master orchestration: Execute Tasks 8 & 9 autonomously via Ollama agents
# Pure autonomous execution - NO human intervention needed

set -euo pipefail

WORKDIR="/mnt/d/ClaudeClockwork"
cd "$WORKDIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Skill-Forge Pipeline: Autonomous Ollama Agent Execution      ║"
echo "║  Tasks: 8 (Generate Documentation) + 9 (Update CHANGELOG)    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

TASK8_RESULT="$WORKDIR/.claude/forge_task8_result.json"
TASK9_RESULT="$WORKDIR/.claude/forge_task9_result.json"

# Ensure results directory exists
mkdir -p "$WORKDIR/.claude"

echo "[1/2] Starting Task 8: Generate FORGE_PIPELINE.md Documentation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ./claudeclockwork/localai/agents/task_8_generate_documentation.sh; then
    echo ""
    echo "✓ Task 8 PASSED"
    TASK8_PASSED=true
else
    echo ""
    echo "✗ Task 8 FAILED"
    TASK8_PASSED=false
fi

echo ""
echo ""
echo "[2/2] Starting Task 9: Update CHANGELOG.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ./claudeclockwork/localai/agents/task_9_update_changelog.sh; then
    echo ""
    echo "✓ Task 9 PASSED"
    TASK9_PASSED=true
else
    echo ""
    echo "✗ Task 9 FAILED"
    TASK9_PASSED=false
fi

echo ""
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    EXECUTION SUMMARY                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Display summary
python3 << 'PYTHON_EOF'
import json
import os

results = {}

# Task 8
task8_file = os.path.expanduser("~/.claude/forge_task8_result.json") if os.path.isfile(os.path.expanduser("~/.claude/forge_task8_result.json")) else "/mnt/d/ClaudeClockwork/.claude/forge_task8_result.json"
if os.path.isfile(task8_file):
    try:
        with open(task8_file) as f:
            data = json.load(f)
            results['task8'] = {
                'success': data.get('success'),
                'task_id': data.get('task_id'),
                'archetype': data.get('archetype')
            }
    except:
        results['task8'] = {'success': False, 'error': 'Could not read result file'}

# Task 9
task9_file = os.path.expanduser("~/.claude/forge_task9_result.json") if os.path.isfile(os.path.expanduser("~/.claude/forge_task9_result.json")) else "/mnt/d/ClaudeClockwork/.claude/forge_task9_result.json"
if os.path.isfile(task9_file):
    try:
        with open(task9_file) as f:
            data = json.load(f)
            results['task9'] = {
                'success': data.get('success'),
                'task_id': data.get('task_id'),
                'archetype': data.get('archetype')
            }
    except:
        results['task9'] = {'success': False, 'error': 'Could not read result file'}

print("Task 8 (Generate Documentation):")
if 'task8' in results:
    print(f"  Status: {'✓ PASS' if results['task8'].get('success') else '✗ FAIL'}")
    print(f"  Task ID: {results['task8'].get('task_id', 'N/A')}")
else:
    print("  Status: ✗ FAIL (no result file)")

print("")
print("Task 9 (Update CHANGELOG):")
if 'task9' in results:
    print(f"  Status: {'✓ PASS' if results['task9'].get('success') else '✗ FAIL'}")
    print(f"  Task ID: {results['task9'].get('task_id', 'N/A')}")
else:
    print("  Status: ✗ FAIL (no result file)")

print("")
both_passed = results.get('task8', {}).get('success') and results.get('task9', {}).get('success')
if both_passed:
    print("OVERALL: ✓ ALL TASKS PASSED")
else:
    print("OVERALL: ✗ SOME TASKS FAILED")
PYTHON_EOF

echo ""
echo "Result files:"
echo "  - Task 8: .claude/forge_task8_result.json"
echo "  - Task 9: .claude/forge_task9_result.json"
echo ""

if $TASK8_PASSED && $TASK9_PASSED; then
    echo "✓ Autonomous execution complete: Both tasks passed"
    exit 0
else
    echo "✗ Autonomous execution complete: Some tasks failed"
    exit 1
fi
