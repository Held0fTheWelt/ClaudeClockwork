# ollama-recovery Skill

A reusable Claude skill for executing complex, multi-phase diagnostic and recovery tasks autonomously.

## Quick Start

**Use case:** You have a structured task plan (Task.md) with multiple phases for diagnosing or recovering a system.

**Trigger:** Ask Claude to "run this task plan using Claude Agents"

**Result:** Each phase executes sequentially, with comprehensive reports for each phase plus a final aggregated report.

## Directory Structure

```
ollama-recovery/
├── SKILL.md                           # Full skill documentation (what users read)
├── README.md                          # This file
├── evals/
│   └── evals.json                    # 3 test cases for validating the skill
└── scripts/
    ├── execute_task_plan.py          # Core implementation
    │   ├── TaskParser                # Parses Task.md files
    │   ├── PhaseExecutor             # Routes phases to Agents
    │   └── TaskExecutor              # Orchestrates full execution
    └── progress_tracker.py            # Real-time progress monitoring
```

## Implementation Overview

### `execute_task_plan.py` (400+ lines)

**TaskParser**
- Reads Task.md using regex patterns
- Extracts mission statement, phase definitions, constraints
- Returns structured data: phases[], constraints[], mission

**PhaseExecutor**
- Takes a phase + context
- Generates Agent briefing with:
  - Phase objectives/tasks
  - All prior phase context
  - Success criteria
- Returns phase report

**TaskExecutor**
- Orchestrates all phases
- Manages context passing between phases
- Generates individual phase reports
- Creates aggregated final report
- Saves TASK_PROGRESS.md in real-time

### `progress_tracker.py` (150+ lines)

**ProgressTracker**
- Monitors execution in real-time
- Tracks findings, files generated, duration per phase
- Writes TASK_PROGRESS.md after each phase
- Provides status updates without interrupting execution

## How It Works

### Phase Execution Flow

```
Input: Task.md with phase definitions
  ↓
Parser.parse() → Extract phases 1-N
  ↓
For each Phase N:
  ├─ Executor.build_context(phase_1...N-1)  # Include all prior context
  ├─ Agent.execute(briefing)                 # Route to Claude Agent
  ├─ Save PHASE_N_*.md                       # Phase report
  └─ ProgressTracker.update()                # Real-time status
  ↓
Final aggregation:
  ├─ Combine all phase reports
  ├─ Create FINAL_REPORT.md
  ├─ List all deliverables
  └─ Return status summary
```

## Test Cases

Three test evals in `evals/evals.json`:

1. **Ollama Recovery (6 phases)** — Original use case, full multi-phase task
2. **PostgreSQL Diagnostics (5 phases)** — Different domain, validates generalization
3. **Single Phase Execution** — Tests partial execution (phase-by-phase)

## Usage Examples

### Example 1: Run all phases of Ollama recovery
```
User: "Run the task plan at C:\WorldOfShadows\Task.md using Claude Agents"

Skill:
  1. Parses Task.md → finds 6 phases
  2. Phase 1 (Agent) → PHASE_01_Assess_current_state.md
  3. Phase 2 (Agent) → PHASE_02_Clean_recovery.md
  4. ... (phases 3-6)
  5. FINAL_REPORT.md with all findings

Result: .ollama/ directory contains:
  PHASE_01_*.md
  PHASE_02_*.md
  ...
  FINAL_REPORT.md
  TASK_PROGRESS.md (real-time updates)
```

### Example 2: Run just one phase
```
User: "Execute phase 3 of the recovery plan (verify GPU/mmap)"

Skill:
  1. Parses Task.md
  2. Finds phase 3
  3. Routes to Agent with context from phases 1-2
  4. Saves PHASE_03_*.md

Result: Single phase report with findings
```

## Key Design Decisions

✅ **Sequential Execution** — Phases run one at a time, no parallelism. Simpler coordination, easier debugging.

✅ **Context Chaining** — Each Agent gets full context from all prior phases. Enables continuity and dependency awareness.

✅ **Real-Time Progress** — TASK_PROGRESS.md updates after each phase. Users can inspect progress without interrupting execution.

✅ **No Agent Interruption** — Once a phase Agent starts, it completes without interruption. Simpler Agent logic, cleaner reports.

✅ **Generalized Task Parser** — Uses regex to extract phases from any Task.md-like document. Not specific to Ollama.

## Integration with Claude

The skill integrates with Claude's Agent tool:

```python
# Inside PhaseExecutor.execute():
agent_tool_call = {
    "subagent_type": "general-purpose",
    "description": "Execute Phase X — [title]",
    "prompt": briefing_text  # Full context + phase objectives
}
```

When invoked, Claude routes the phase execution to an independent Agent with:
- Full mission context
- All prior phase results
- Current phase tasks
- Success criteria

## Files Generated During Execution

Each execution produces:

```
<project-root>/
├── PHASE_01_Assess_current_state.md
├── PHASE_02_Clean_recovery.md
├── PHASE_03_Verify_GPU_and_mmap.md
├── PHASE_04_Establish_safe_mode.md
├── PHASE_05_Validate_with_tests.md
├── PHASE_06_Final_report.md
├── FINAL_REPORT.md                   # Aggregated summary
└── TASK_PROGRESS.md                  # Real-time progress
```

## Error Handling

- **Missing Task.md**: Error message, suggest checking path
- **Invalid phase format**: Warning logged, phase skipped
- **Agent failure**: Document failure, suggest remediation, stop execution
- **Partial completion**: FINAL_REPORT shows which phases succeeded/failed

## Future Enhancements

Possible improvements (not yet implemented):

- [ ] Parallel phase execution (with dependency tracking)
- [ ] Rollback support (undo changes from failed phase)
- [ ] Phase retry logic (auto-retry failed phases N times)
- [ ] Phase dependencies (execute phases in defined order, not just sequentially)
- [ ] Integration with external monitoring (Prometheus, DataDog alerts)
- [ ] Historical tracking (keep archive of all execution reports)

## Testing

Run test evals:

```bash
cd <skill-path>
python3 scripts/execute_task_plan.py evals/test_task.md ./test_output/
```

Or validate with the skill-creator framework:

```bash
# (From skill-creator directory)
python3 -m scripts.run_eval \
  --skill ollama-recovery \
  --eval-set evals/evals.json
```

## Troubleshooting

**"Phase timed out"** — Agent took too long. Check phase complexity, increase timeout.

**"Missing phase definitions"** — Task.md format issue. Ensure phases are labeled `Phase 1 — Title`, `Phase 2 — Title`, etc.

**"Agent returned empty report"** — Agent didn't complete. Check Agent logs for errors.

**"Files not generated"** — Check output directory permissions.

---

**Created:** March 2026
**Author:** Claude Code (auto-generated skill)
**Status:** Production-ready
