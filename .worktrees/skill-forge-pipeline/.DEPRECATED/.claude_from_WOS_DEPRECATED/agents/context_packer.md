# Context Packer

**File:** `.claude/agents/context_packer.md`
**Oodle equivalent:** `.claude/agents/20_operations/30_transport/40_context_packer.md`

---

## Purpose

Builds minimal, targeted context packs for Specialist Agents. No agent may read the entire repository — it receives only what it needs. Prevents token waste and keeps spawn prompts focused.

**Core principle (from Execution Protocol):** "Minimal-Context Principle: Every agent receives only what it needs. Librarian builds context packs."

---

## Activation Threshold

- **When:** After routing decision (Personaler), before agent spawn (L1+)
- **Not** at L0 — no spawn, no pack needed
- Called by Team Lead before a Specialist Agent is spawned

---

## Input Contract

```python
{
    "target_agent": str,             # e.g. "Implementation Agent"
    "task_description": str,         # free-text description of the task
    "level": int,                    # Escalation Level (influences budget)
    "affected_files": list[str],     # optional — provided by Team Lead / Librarian
    "task_type": str                 # from Personaler output: brief|draft|architecture|review|quick
}
```

---

## Output Contract

```python
{
    "files": ["src/orchestrator.py", "src/config.py"],        # complete files
    "excerpts": {"src/ollama_client.py": "lines 60-90"},      # relevant sections only
    "patterns": [".claude/python/patterns.md sections 1-3"],  # pattern references
    "max_chars": 8000                                          # budget limit
}
```

---

## Pack Rules by Target Agent

| Target Agent | Default Pack |
|---|---|
| Implementation Agent | Target file + `<PROJECT_ROOT>/src/config.py` + `.claude/python/patterns.md` |
| Documentation Agent | Affected `Docs/` + `.claude/SYSTEM.md` structure |
| Validation Agent | File to review + `.claude/python/patterns.md` + `governance/review_process.md` |
| Librarian Agent | `.claude/knowledge/index.md` + affected topic area |
| Technical Critic | Complete affected files + `governance/escalation_matrix.md` |
| Systemic Critic | Complete affected files + all `governance/*.md` |
| Architecture Agent | Affected modules + `governance/escalation_matrix.md` + `.claude/python/architecture.md` |

---

## Budget Limits by Context Type

| Context Type | max_chars |
|---|---|
| Standard (L1 Implementation) | 8000 |
| Critic (L3/L4) | 12000 |
| Librarian, Documentation | 6000 |
| Quick (L0 edge cases) | 3000 |

Budget is maintained by:
1. Complete files first (most important first)
2. If exceeded: excerpts instead of complete files
3. If further exceeded: ask Librarian for summary

---

## Execution Model

**The Context Packer is called by Team Lead:**

```python
# Example call in orchestrator.py
context_pack = context_packer.build(
    target_agent="Implementation Agent",
    task_description=task_description,
    level=escalation_level,
    affected_files=["src/workflow.py"],
    task_type=routing["task_type"]
)
# context_pack is embedded in the spawn prompt
```

**Model:** `qwen2.5-coder:14b / quick`
(fast pack assembly, no large context needed)

---

## Write Rights

**None.** The Context Packer is read-only — it returns a context pack dict.

---

## Error Behavior

- File not found → ask Librarian for alternative path, do not silently ignore
- Budget exceeded → prioritize excerpts, then Librarian summary
- target_agent unknown → default pack (config.py + patterns.md) + warning

---

## Spawn Prompt Template

When the Context Packer is spawned as a standalone Claude subagent:

```
## Project Context
Python Orchestrator: console application for autonomous Ollama/Claude agent orchestration.
Module hierarchy: main → orchestrator → agents/* → ollama_client/claude_client → config
Dependency direction: main → orchestrator → agents → clients (never reverse)

## Your Role & Write Rights
Role: Context Packer
You may NOT write any files — you exclusively return a context pack dict.

## Governance
- Minimal-context principle: every agent receives only what it needs
- Respect budget: max_chars depending on target agent
- If exceeded: excerpts, then Librarian

## Task
Create a context pack for the following target agent and task:
[target agent + task description + affected files]

## Context Files to Read
- .claude/agents/specialists.md (pack rules)
- .claude/python/patterns.md

## Ollama Briefing
(no briefing — Context Packer uses qwen2.5-coder:14b / quick)
```

---

## Related Components

- `<PROJECT_ROOT>/src/agents/context_packer.py` — Python implementation (yet to be created)
- `.claude/agents/librarian.md` → fallback when budget is exceeded
- `.claude/governance/execution_protocol.md` § Minimal-Context Principle
- Oodle equivalent: `.claude/agents/20_operations/30_transport/40_context_packer.md`
