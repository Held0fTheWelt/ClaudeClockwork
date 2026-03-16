---
name: ollama-recovery
description: Execute multi-phase diagnostic, recovery, and stabilization tasks autonomously. Use this skill when you have a structured task plan (like Task.md) that outlines sequential phases for diagnosing system issues, recovering from failures, or stabilizing services. This skill will coordinate Claude Agents to execute each phase independently, generate comprehensive reports, track progress, and produce final deliverables. Ideal for infrastructure recovery, service stabilization, system diagnostics, and complex troubleshooting workflows. Trigger whenever the user mentions running a "task plan", "phase-based recovery", "multi-step diagnostic", or provides a Task.md-like document.
compatibility: Requires Agent tool, file read/write capabilities, bash execution
---

# Multi-Phase Task Execution Skill

## Overview

This skill automates the execution of complex, multi-phase technical tasks — particularly diagnostic and recovery workflows. It coordinates Claude Agents to execute each phase independently, tracks progress, generates reports, and produces final deliverables.

**Common use cases:**
- Ollama runtime recovery and stabilization
- System diagnostics (CPU, memory, GPU issues)
- Service recovery workflows
- Infrastructure troubleshooting
- Performance optimization workflows

## How It Works

The skill uses three bundled Python scripts working in concert:

### **1. TaskParser** (execute_task_plan.py)
- Reads Task.md using regex extraction
- Extracts: mission statement, phase definitions, constraints
- Builds context for each phase including all prior phases
- Provides phase-by-phase data structure

### **2. PhaseExecutor** (execute_task_plan.py)
- Takes a parsed phase + accumulated context
- Routes to Claude Agent with full briefing
- Agent executes phase tasks autonomously
- Returns phase report with findings

### **3. ProgressTracker** (progress_tracker.py)
- Monitors execution in real-time
- Writes TASK_PROGRESS.md after each phase
- Tracks findings, files generated, duration
- Allows inspection of progress at any time

### Execution Flow

```
User: "Run Task.md with Claude Agents"
        ↓
    TaskParser reads and parses Task.md
        ↓
    For each Phase:
        ↓
        PhaseExecutor routes to Agent with:
            - Phase objectives
            - Full accumulated context (this + all prior phases)
            - Previous results
        ↓
        Agent executes phase tasks
        ↓
        Report written to PHASE_N_*.md
        ↓
        ProgressTracker updates TASK_PROGRESS.md
        ↓
    Final aggregation:
        - Combine all phase reports
        - Write FINAL_REPORT.md
        - List deliverables
```

## Usage

### Basic Workflow

```
User: "Run the updated Task.md with your Claude Agents"
↓
Skill parses Task.md
↓
Skill executes Phase 1 (Agent receives full context)
↓
Skill executes Phase 2 (Agent has Phase 1 results as context)
↓
... (continues through all phases)
↓
Skill aggregates final report
↓
Returns: Phase summaries + deliverables
```

### Input Requirements

**Required:**
- Path to Task.md or similar task specification file
- File must contain:
  - Mission/objective statement
  - Phase definitions (Phase 1, Phase 2, etc.)
  - Objectives and tasks for each phase
  - Success criteria/acceptance criteria

**Optional:**
- Configuration file with constraints/preferences
- Previous state or logs from prior attempts
- System-specific context

### Output Format

The skill produces:

```
<project-root>/
├── PHASE_N_REPORT.md          # For each phase
├── PHASE_N_EXECUTION_SUMMARY.md
├── FINAL_REPORT.md            # Aggregated results
├── TASK_COMPLETION_STATUS.md  # Success/fail summary
└── DELIVERABLES_MANIFEST.md   # Where outputs are located
```

Each report includes:
- Phase name and objectives
- Tasks executed
- Results/findings
- Success metrics
- Next steps
- Files created

## Execution Philosophy

**Autonomy First**: Each phase Agent works independently with full context. Agents are not interrupted mid-phase.

**Progress Tracking**: After each phase, the skill updates a progress file so you can see what's completed even if interrupted.

**Documentation**: Every phase generates a report. No silent failures — all errors and warnings are documented.

**Dependency Management**: Later phases receive earlier phase results as context, enabling continuity.

**Fail-Safe**: If a phase fails:
1. Document the failure thoroughly
2. Provide diagnostic output
3. Suggest remediation
4. Don't automatically proceed to next phase

## Command Structure

### Invoke with explicit task path:
```
Run the task plan at /path/to/Task.md using Claude Agents
```

### Invoke with Task.md in current directory:
```
Execute Task.md with Claude Agents. Run all phases.
```

### Invoke for a specific phase:
```
Run Phase 3 of the task plan (Phase X — Verify GPU and mmap configuration)
```

## Key Features

### 1. Automatic Phase Sequencing
- Reads phase definitions from Task.md
- Executes phases in order
- Respects phase dependencies
- Stops on critical failures

### 2. Agent Context Management
- Each Agent receives full context from previous phases
- Agents don't need to re-read parent task — just focus on their phase
- Results automatically passed to next phase

### 3. Progress Tracking
- Creates `TASK_PROGRESS.md` during execution
- Updates after each phase completes
- Shows what's done, what's next, what failed

### 4. Comprehensive Reporting
- Phase reports with findings and recommendations
- Final aggregated report with executive summary
- Deliverables manifest showing where outputs are stored
- Timing and resource metrics

### 5. Error Handling
- Documents all errors without hiding them
- Provides diagnostic output
- Suggests recovery steps
- Continues gracefully on non-critical failures

## Example: Ollama Recovery

**Input:** Task.md with 6 phases (Assess → Clean → Verify → Configure → Validate → Report)

**Execution:**
```
Phase 1 Agent → Diagnoses Ollama state → Creates PHASE1_REPORT.md
Phase 2 Agent → Uses Phase 1 findings → Executes recovery → Creates PHASE2_REPORT.md
Phase 3 Agent → Uses Phase 1-2 results → Verifies GPU/mmap → Creates PHASE3_REPORT.md
... (etc)
Phase 6 Agent → Aggregates all findings → Creates FINAL_REPORT.md
```

**Output:**
```
PHASE_1_DIAGNOSTIC_SUMMARY.md
PHASE_2_CLEAN_RECOVERY.md
PHASE_3_GPU_MMAP_VERIFICATION.md
PHASE_4_SAFE_MODE_CONFIGURATION.md
PHASE_5_VALIDATION_TESTING.md
PHASE_6_FINAL_REPORT.md
OLLAMA_DAILY_OPERATIONS.md
OLLAMA_EMERGENCY_RECOVERY.md
```

## Constraints & Assumptions

- Task.md must have clear phase definitions
- Each phase must have defined objectives
- Phases should be mostly independent (can parallelize future versions)
- Task should be automatable (not requiring human intervention mid-phase)
- System must support Agent tool execution

## Usage: How to Trigger the Skill

The skill activates when you provide or reference a structured task plan. Natural triggers:

```
"Run the task plan at C:\path\to\Task.md using Claude Agents"
"Execute this multi-phase recovery plan with autonomous agents"
"Run all phases of the diagnostic workflow"
"Execute phase 3 of the Ollama recovery plan"
```

### What happens:

1. **Parser** reads your Task.md and extracts phases
2. **Router** sends each phase to a Claude Agent with full context
3. **Executor** orchestrates sequential execution with context-passing
4. **Tracker** updates progress after each phase
5. **Aggregator** combines all reports into final deliverables

**Outputs appear in:** Same directory as your Task.md
- `PHASE_1_*.md`, `PHASE_2_*.md`, etc. (one per phase)
- `FINAL_REPORT.md` (aggregated summary)
- `TASK_PROGRESS.md` (updated in real-time during execution)

## When to Use This Skill

✅ **Use this skill for:**
- Multi-phase diagnostic workflows
- System recovery and stabilization
- Structured troubleshooting procedures
- Complex infrastructure tasks
- Documented runbooks/playbooks

❌ **Don't use this skill for:**
- Single-phase, simple tasks (too heavyweight)
- Real-time interactive troubleshooting (humans need to be in the loop)
- Tasks requiring user approval between phases (design for autonomous execution)
- Unstructured problems without a documented plan

## How Agents Are Used

Each phase receives:
1. **Full Task Context**: The entire Task.md + Mission statement
2. **Previous Results**: All prior phase outputs and findings
3. **Current Phase Details**: Specific objectives and tasks for this phase
4. **Constraints**: Any limitations or guardrails mentioned in Task.md

The Agent is expected to:
- Work autonomously without interruption
- Document findings comprehensively
- Produce outputs in the specified format
- Report status accurately (success/partial/failed)

## Integration with Your Workflow

This skill pairs well with:
- **Task.md files** in project root (structured task plans)
- **Git repositories** (for version control of reports)
- **Monitoring/observability** tools (logs, dashboards)
- **CI/CD pipelines** (can be invoked by automation)

---

**Note**: This skill is best suited for diagnostic, recovery, and validation tasks. If you're building something new from scratch, simpler workflows may be more appropriate.
