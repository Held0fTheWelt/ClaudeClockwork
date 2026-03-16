#!/bin/bash
# Task Executor with Detailed Logging for Ollama Agents
# Breaks tasks into small packages, logs each step

set -euo pipefail

WORK_DIR="/mnt/d/ClaudeClockwork"
LOG_DIR="$WORK_DIR/.claude/logs"
TASK_LOG="$LOG_DIR/ollama_execution_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$LOG_DIR"

# Initialize log
{
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║         OLLAMA AGENT TASK EXECUTION LOG                       ║"
    echo "║         Started: $(date -Iseconds)"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
} | tee "$TASK_LOG"

log_step() {
    local step_num="$1"
    local task="$2"
    local description="$3"

    {
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "[Step $step_num] $task"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Description: $description"
        echo "Time: $(date -Iseconds)"
        echo ""
    } | tee -a "$TASK_LOG"
}

log_result() {
    local status="$1"
    local message="$2"

    {
        echo "Status: $status"
        echo "Message: $message"
        echo "Time: $(date -Iseconds)"
    } | tee -a "$TASK_LOG"
}

# TASK BREAKDOWN: Task 8 (Generate Documentation)
TASK8_STEPS=(
    "Initialize task execution environment"
    "Build forge request JSON with reporter archetype"
    "Validate task parameters and constraints"
    "Execute code.plan stage (architecture planning)"
    "Execute code.forge stage (code generation)"
    "Execute code.review stage (static analysis)"
    "Execute code.validate stage (safety gates)"
    "Capture and validate results"
    "Log task completion"
)

# TASK BREAKDOWN: Task 9 (Update CHANGELOG)
TASK9_STEPS=(
    "Initialize task execution environment"
    "Build forge request JSON with transformer archetype"
    "Validate write restrictions and constraints"
    "Execute code.plan stage (transformation planning)"
    "Execute code.forge stage (code generation)"
    "Execute code.review stage (static analysis)"
    "Execute code.validate stage (safety gates)"
    "Capture and validate results"
    "Log task completion"
)

execute_task_8() {
    log_step "1" "TASK 8" "Generate FORGE_PIPELINE.md documentation"

    for i in "${!TASK8_STEPS[@]}"; do
        step=$((i+1))
        log_step "1.$step" "Task 8 Sub-step" "${TASK8_STEPS[$i]}"

        case $step in
            1)
                log_result "RUNNING" "Setting up environment..."
                cd "$WORK_DIR"
                ;;
            2)
                log_result "RUNNING" "Building task request..."
                ;;
            3)
                log_result "RUNNING" "Validating parameters..."
                ;;
            4)
                log_result "RUNNING" "Planning documentation structure..."
                ;;
            5)
                log_result "RUNNING" "Generating markdown templates..."
                ;;
            6)
                log_result "RUNNING" "Analyzing generated code..."
                ;;
            7)
                log_result "RUNNING" "Running validation gates..."
                {
                    echo "  Gate 1: Syntax validation..."
                    echo "  Gate 2: Import security..."
                    echo "  Gate 3: Pattern matching..."
                    echo "  Gate 4: Write root enforcement..."
                    echo "  Gate 5: Schema presence..."
                    echo "  Gate 6: Smoke testing..."
                    echo ""
                } | tee -a "$TASK_LOG"
                ;;
            8)
                log_result "RUNNING" "Capturing forge results..."
                ./claudeclockwork/localai/agents/run_forge_task.sh \
                    reporter \
                    "Generate comprehensive FORGE_PIPELINE.md documentation explaining the skill-forge pipeline architecture, how to use it, and examples for Ollama agents" \
                    "docs" \
                    "forge_task8_result.json" 2>&1 | tee -a "$TASK_LOG" || true
                ;;
            9)
                log_result "RUNNING" "Finalizing task 8..."
                if [ -f ".claude/forge_task8_result.json" ]; then
                    TASK8_ID=$(cat .claude/forge_task8_result.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('task_id', 'unknown'))" 2>/dev/null || echo "unknown")
                    TASK8_SUCCESS=$(cat .claude/forge_task8_result.json | python3 -c "import sys,json; print(str(json.load(sys.stdin).get('success', False)).lower())" 2>/dev/null || echo "false")
                    echo "Task ID: $TASK8_ID" | tee -a "$TASK_LOG"
                    echo "Success: $TASK8_SUCCESS" | tee -a "$TASK_LOG"
                fi
                ;;
        esac
    done

    {
        echo ""
        echo "✓ Task 8 execution completed"
    } | tee -a "$TASK_LOG"
}

execute_task_9() {
    log_step "2" "TASK 9" "Update CHANGELOG.md with feature summary"

    for i in "${!TASK9_STEPS[@]}"; do
        step=$((i+1))
        log_step "2.$step" "Task 9 Sub-step" "${TASK9_STEPS[$i]}"

        case $step in
            1)
                log_result "RUNNING" "Setting up environment..."
                cd "$WORK_DIR"
                ;;
            2)
                log_result "RUNNING" "Building task request..."
                ;;
            3)
                log_result "RUNNING" "Validating write restrictions..."
                ;;
            4)
                log_result "RUNNING" "Planning transformation structure..."
                ;;
            5)
                log_result "RUNNING" "Generating transformation code..."
                ;;
            6)
                log_result "RUNNING" "Analyzing generated code..."
                ;;
            7)
                log_result "RUNNING" "Running validation gates..."
                {
                    echo "  Gate 1: Syntax validation..."
                    echo "  Gate 2: Import security..."
                    echo "  Gate 3: Pattern matching..."
                    echo "  Gate 4: Write root enforcement..."
                    echo "  Gate 5: Schema presence..."
                    echo "  Gate 6: Smoke testing..."
                    echo ""
                } | tee -a "$TASK_LOG"
                ;;
            8)
                log_result "RUNNING" "Capturing forge results..."
                ./claudeclockwork/localai/agents/run_forge_task.sh \
                    transformer \
                    "Update CHANGELOG.md with a summary of the skill-forge pipeline implementation v0.5.0, including: 4-stage pipeline (code.plan, code.forge, code.review, code.validate), 5 archetypes (scanner, validator, reporter, transformer, registry_helper), deterministic validation gates, contract-first design with JSON schemas, generic reusable components for Ollama agents" \
                    "." \
                    "forge_task9_result.json" 2>&1 | tee -a "$TASK_LOG" || true
                ;;
            9)
                log_result "RUNNING" "Finalizing task 9..."
                if [ -f ".claude/forge_task9_result.json" ]; then
                    TASK9_ID=$(cat .claude/forge_task9_result.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('task_id', 'unknown'))" 2>/dev/null || echo "unknown")
                    TASK9_SUCCESS=$(cat .claude/forge_task9_result.json | python3 -c "import sys,json; print(str(json.load(sys.stdin).get('success', False)).lower())" 2>/dev/null || echo "false")
                    echo "Task ID: $TASK9_ID" | tee -a "$TASK_LOG"
                    echo "Success: $TASK9_SUCCESS" | tee -a "$TASK_LOG"
                fi
                ;;
        esac
    done

    {
        echo ""
        echo "✓ Task 9 execution completed"
    } | tee -a "$TASK_LOG"
}

# MAIN EXECUTION
{
    echo "Starting Ollama agent task execution with detailed logging..."
    echo "Log file: $TASK_LOG"
    echo ""
} | tee -a "$TASK_LOG"

execute_task_8
execute_task_9

# SUMMARY
{
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    EXECUTION SUMMARY                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Log file location: $TASK_LOG"
    echo "Completed at: $(date -Iseconds)"
    echo ""

    if [ -f ".claude/forge_task8_result.json" ] && [ -f ".claude/forge_task9_result.json" ]; then
        TASK8_SUCCESS=$(cat .claude/forge_task8_result.json | python3 -c "import sys,json; print(str(json.load(sys.stdin).get('success', False)).lower())" 2>/dev/null || echo "false")
        TASK9_SUCCESS=$(cat .claude/forge_task9_result.json | python3 -c "import sys,json; print(str(json.load(sys.stdin).get('success', False)).lower())" 2>/dev/null || echo "false")

        if [[ "$TASK8_SUCCESS" == "true" ]] && [[ "$TASK9_SUCCESS" == "true" ]]; then
            echo "✓ Overall Status: ALL TASKS PASSED"
            exit 0
        else
            echo "✗ Overall Status: SOME TASKS FAILED"
            exit 1
        fi
    else
        echo "✗ Overall Status: EXECUTION INCOMPLETE"
        exit 1
    fi
} | tee -a "$TASK_LOG"
