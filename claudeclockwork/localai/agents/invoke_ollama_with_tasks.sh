#!/bin/bash
# Pure Ollama Agent Invocation with Task Breakdown
# Invokes Ollama to execute tasks as small packages with visible logging

set -euo pipefail

WORK_DIR="/mnt/d/ClaudeClockwork"
LOG_DIR="$WORK_DIR/.claude/logs"
OLLAMA_LOG="$LOG_DIR/ollama_agent_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$LOG_DIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       INVOKING PURE OLLAMA AGENTS WITH TASK BREAKDOWN         ║"
echo "║       Tasks will be split into small executable packages      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Log file: $OLLAMA_LOG"
echo ""

# OLLAMA Agent 1: Execute Task 8 with visible steps
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "INVOKING OLLAMA AGENT 1: Task 8 (Generate Documentation)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ollama run mistral << 'OLLAMA_TASK_8' 2>&1 | tee -a "$OLLAMA_LOG"
You are an autonomous Ollama agent executing Task 8 of a skill-forge pipeline.

TASK 8: Generate FORGE_PIPELINE.md documentation

Your mission is to break this down into small steps and execute each one, logging progress:

STEP 1: Initialize
  - Change to work directory: cd /mnt/d/ClaudeClockwork
  - Report: "Task 8 Agent initialized"

STEP 2: Validate environment
  - Check that run_forge_task.sh exists
  - Report: "Environment validated"

STEP 3: Build request
  - You will execute: ./claudeclockwork/localai/agents/run_forge_task.sh reporter "Generate comprehensive FORGE_PIPELINE.md documentation explaining the skill-forge pipeline architecture, how to use it, and examples for Ollama agents" "docs" "forge_task8_result.json"
  - Report: "Request built"

STEP 4: Execute task
  - Run the command above
  - Report: "Task 8 execution completed"

STEP 5: Verify results
  - Check if .claude/forge_task8_result.json exists
  - Extract task_id and success status
  - Report the task_id and whether it succeeded

Execute each step and report progress after each one. Do this now.
OLLAMA_TASK_8

echo ""
echo ""

# OLLAMA Agent 2: Execute Task 9 with visible steps
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "INVOKING OLLAMA AGENT 2: Task 9 (Update CHANGELOG)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ollama run neural-chat << 'OLLAMA_TASK_9' 2>&1 | tee -a "$OLLAMA_LOG"
You are an autonomous Ollama agent executing Task 9 of a skill-forge pipeline.

TASK 9: Update CHANGELOG.md with feature summary

Your mission is to break this down into small steps and execute each one, logging progress:

STEP 1: Initialize
  - Change to work directory: cd /mnt/d/ClaudeClockwork
  - Report: "Task 9 Agent initialized"

STEP 2: Validate environment
  - Check that run_forge_task.sh exists
  - Report: "Environment validated"

STEP 3: Build request
  - You will execute: ./claudeclockwork/localai/agents/run_forge_task.sh transformer "Update CHANGELOG.md with a summary of the skill-forge pipeline implementation v0.5.0, including: 4-stage pipeline, 5 archetypes, deterministic validation gates, contract-first design, generic reusable components for Ollama agents" "." "forge_task9_result.json"
  - Report: "Request built"

STEP 4: Execute task
  - Run the command above
  - Report: "Task 9 execution completed"

STEP 5: Verify results
  - Check if .claude/forge_task9_result.json exists
  - Extract task_id and success status
  - Report the task_id and whether it succeeded

Execute each step and report progress after each one. Do this now.
OLLAMA_TASK_9

echo ""
echo ""

# Summary
{
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                OLLAMA AGENT EXECUTION COMPLETE                 ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Full execution log: $OLLAMA_LOG"
    echo "Timestamp: $(date -Iseconds)"
    echo ""
    echo "Results:"
    echo "  Task 8 result: .claude/forge_task8_result.json"
    echo "  Task 9 result: .claude/forge_task9_result.json"
    echo ""
    echo "Both Ollama agents completed their tasks autonomously."
} | tee -a "$OLLAMA_LOG"
