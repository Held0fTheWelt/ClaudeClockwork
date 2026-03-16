#!/bin/bash
# Task 8: Generate FORGE_PIPELINE.md documentation
# Autonomous Ollama agent execution - NO HUMAN INTERVENTION

set -euo pipefail

WORKDIR="/mnt/d/ClaudeClockwork"
cd "$WORKDIR"

echo "========================================"
echo "Task 8: Generate FORGE_PIPELINE.md"
echo "Executing: Pure Ollama Agent"
echo "========================================"
echo ""

# Execute forge pipeline to generate documentation
./claudeclockwork/localai/agents/run_forge_task.sh \
  reporter \
  "Generate comprehensive FORGE_PIPELINE.md documentation explaining the skill-forge pipeline architecture, how to use it, and examples for Ollama agents" \
  "docs" \
  ".claude/forge_task8_result.json"

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Task 8 Completed Successfully"
    echo ""

    # Parse and display result summary
    if [ -f ".claude/forge_task8_result.json" ]; then
        echo "Result saved to: .claude/forge_task8_result.json"
        python3 -c "
import json
with open('.claude/forge_task8_result.json') as f:
    result = json.load(f)
    if result.get('success'):
        print('Status: SUCCESS')
        print('Task ID:', result.get('task_id'))
        print('Archetype:', result.get('archetype'))
    else:
        print('Status: FAILED')
        print('Reason:', result.get('result', {}).get('reason', 'Unknown'))
" 2>/dev/null || true
    fi

    exit 0
else
    echo ""
    echo "✗ Task 8 Failed"
    if [ -f ".claude/forge_task8_result.json" ]; then
        cat .claude/forge_task8_result.json | python3 -m json.tool 2>/dev/null || cat .claude/forge_task8_result.json
    fi
    exit 1
fi
