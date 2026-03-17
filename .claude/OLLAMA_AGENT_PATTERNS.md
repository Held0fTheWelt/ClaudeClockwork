# Ollama Agent Execution Patterns & Knowledgebase

**Purpose:** Document what works best and what doesn't work for pure Ollama agents across all projects.

**Last Updated:** 2026-03-17

---

## Core Rules (Non-Negotiable)

1. **One agent at a time** - Never dispatch multiple Ollama agents in parallel
2. **Pure Ollama only** - Never use Claude agents on implementation tasks
3. **No self-implementation** - Orchestrators never implement code, only orchestrate Ollama agents
4. **Tasks, not code** - Give Ollama agents task descriptions; they decide implementation approach

---

## What Works Well ✅

### Task Specification
- **Exact steps with file paths** - Agent executes step-by-step instructions reliably
- **Reference to plan documents** - Point agent to detailed specs in docs/superpowers/plans/
- **Success criteria** - Clear definition of "done" (tests pass, commit messages, verification)
- **Examples in the prompt** - Show what expected output looks like
- **Absolute paths** - Use /mnt/d/ or /mnt/c/ full paths, never relative

### Prompt Structure
- **Context first** - Explain WHERE task fits in larger project
- **Step-by-step** - Break into small, sequential actions
- **One task per dispatch** - Fresh Ollama agent per logical task
- **CRITICAL: ACTUALLY DOING IT** - Start with "You are NOT explaining. You are ACTUALLY DOING these steps."
- **End with status request** - Always ask for: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED

### Code Tasks
- **Test-driven** - Tests first, implementation after, verify all pass
- **Exact code in prompt** - Paste full code to CREATE/MODIFY, don't make agent read
- **File creation/modification** - Use precise language: "CREATE file at...", "MODIFY..."
- **Git commits** - Agent commits after each task
- **Manual testing** - Agent runs commands to verify behavior

### Testing & Verification
- **pytest for Python** - Ollama agents understand pytest output
- **CLI command testing** - Direct `python script.py arg` commands work well
- **JSON validation** - Testing JSON output is reliable
- **Exit codes** - Agents understand and verify process exit codes

---

## What Doesn't Work ❌

### Avoid These Patterns
- **Multiple agents in parallel** - Causes conflicts, confusion
- **"Explain the steps" language** - Agent outlines instead of doing
- **Vague task descriptions** - "implement the feature" without steps → stuck
- **Asking agent to decide architecture** - Architecture in the plan, not agent's choice
- **Interactive prompts** - Don't ask "what should we do?"
- **Reading large files** - Provide extracted sections from plans
- **Implementer orchestrating** - If orchestrator is Claude, defeats pure Ollama goal
- **Timeout patience** - Allow 5-10 minutes for complex tasks

### Problem Scenarios
- **ANSI codes in output** - Corrupts JSON (already fixed in OllamaAgent)
- **Context window overflow** - Focused task < 5 min complexity
- **Model too small** - qwen2.5-14b:agent minimum; phi models inadequate
- **Output file empty after timeout** - Agent still running, check process

---

## Model Recommendations

### Current Best: `qwen2.5-14b:agent`
- ✅ Code generation quality
- ✅ Instruction following
- ✅ JSON output handling
- ✅ Test execution understanding
- ✅ Git workflow competence
- ⏱️ ~10GB, reasonable speed

### Also Available
- `qwen3.5-35b:agent` - Higher quality, larger (35GB)
- `phi` models - Faster but lower quality, not recommended

---

## Task Execution Checklist

Before dispatching Ollama agent:

- [ ] Task description is clear and actionable
- [ ] **CRITICAL: Starts with "You are NOT explaining. You are ACTUALLY DOING..."**
- [ ] File paths are absolute (/mnt/d/... or /mnt/c/...)
- [ ] Reference to plan document provided
- [ ] **Step-by-step instructions with exact code (if code task)**
- [ ] Success criteria defined
- [ ] Expected output examples given
- [ ] No parallel agent attempts (one at a time)
- [ ] Prompt ends with status request

---

## Escalation Criteria

### BLOCKED Status
Agent cannot proceed:
- Is the plan missing required info?
- Is a tool/dependency missing?
- Is the task fundamentally too large?
- **Do NOT retry same agent** - diagnose and either fix plan or break task

### NEEDS_CONTEXT Status
Agent needs missing information:
- Provide context clearly
- Re-dispatch SAME agent with added context
- Add to prompt, don't make agent re-read files

### DONE_WITH_CONCERNS Status
Task complete but agent has doubts:
- Read the concerns
- If correctness issue: have agent verify
- If observation: note and proceed to review

---

## Quality First

From the orchestrator's instructions: "Time is not a problem. Quality is."

**Apply this by:**
1. **Review knowledgebase before adjusting approach** - Check patterns.md if agent struggles
2. **Single agent per task** - Quality > speed
3. **Explicit instructions** - "ACTUALLY DOING" language prevents outline-only responses
4. **Verification steps** - Tests, CLI checks, commits confirm quality
5. **Patient waits** - 5-10 minutes for complex Ollama work is normal

---

## Project Patterns

### WorldOfShadows + ClaudeClockwork Integration

**Mode System:**
- Current mode in: `/mnt/d/ClaudeClockwork/.claude/state/mode_state.json`
- Check before dispatch: `cat /mnt/d/ClaudeClockwork/.claude/state/mode_state.json | grep active_mode`
- Should show: `"active_mode": "default"` for pure Ollama

**Shared Knowledgebase:**
- This file location: `/mnt/d/ClaudeClockwork/.claude/OLLAMA_AGENT_PATTERNS.md`
- Accessible across projects
- Update when new patterns discovered

---

## Examples of Success

### ✅ Task Pattern (Template for Success)
```
TASK N: IMPLEMENT [Feature Name]

Working directory: /mnt/c/...

CRITICAL: You are NOT explaining steps. You are ACTUALLY DOING them.

## Step 1: CREATE file at path/to/file

Create file at: [exact path]
Use this EXACT code:
[full code snippet]

## Step 2: RUN command

Command: [exact command]
Expected: [expected output/behavior]

## Step 3: TEST

Command: [test command]
Expected: [test results]

... (continue steps)

## WHEN DONE

Report status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
```

---

## Learning Log

**Discovered Patterns:**
- Ollama agents need explicit "ACTUALLY DOING" framing or they outline instead of implement
- Step-by-step with exact code in prompt prevents agent from getting lost
- Timeout of 5+ minutes is normal for complex code tasks
- Absolute file paths eliminate confusion
- One agent at a time maintains context integrity

**Timing Observations:**
- Simple task (create one file): 30 seconds
- Medium task (implement + test): 2-3 minutes
- Complex task (full feature): 5-10 minutes

---

## Related Files

- `/mnt/d/ClaudeClockwork/claudeclockwork/core/agents/ollama_agent.py` - OllamaAgent implementation
- `/mnt/d/ClaudeClockwork/.claude/state/mode_state.json` - Current execution mode
- Project plans in `docs/superpowers/plans/` - Reference specifications

---
