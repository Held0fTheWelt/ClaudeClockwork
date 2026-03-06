# Execution Protocol — Python Orchestrator

> Mandatory execution protocol for Claude Code and all agent spawns.
> Applies to all tasks regardless of trigger.

---

## Step 1 — Read Canonical Sources

Always read first:
1. `CLAUDE.md` + `.claude/SYSTEM.md` — Project identity, module hierarchy, patterns
2. `.project/MEMORY.md` — Stable cross-session knowledge (Team Lead reads this first)
3. `governance/workflow_triggers.md` — Trigger routing, document naming

---

## Step 2 — Classify Task

Determine escalation level (→ `governance/decision_policy.md`):

| Level | Who decides | Typical situation |
|---|---|---|
| L0 | Specialist autonomous | 1 file, no API change |
| L1 | Team Lead | 2–5 files, clearly bounded |
| L2 | Architecture Agent | New module, new dependency |
| L3 | Technical Critic | Performance paths, external API |
| L4 | Systemic Critic | Governance changes, new agent types |
| **L5** | **User — STOP and ask** | Orchestrator redesign, backend switch |

**Choose smallest sufficient model size** (→ Ollama hardware routing in `ollama_integration.md`).

---

## Step 3 — Check L5 Gates (Before Any Action)

**User confirmation mandatory for:**
- External providers or API keys
- Requested tool autonomy (automated bash execution)
- Destructive operations or large refactors
- Persistent disagreement after critic review
- Core orchestrator redesign or LLM backend switch

---

## Step 4 — Work in Small, Verifiable Steps

**Execution phases** (in this order):

```
intake → plan → build → validate → review → docs → archive
```

- **intake (low-effort servant)**: Recognize trigger, capture subject, load context (Librarian) and structure it. Preparation only: collect sources, identify affected files/diffs, brief intake note. **No** evaluation, no architecture decisions.
- **plan**: Create plan document (`.project/Docs/Plans/Plan_<Name>.md`), user approval
- **build**: Implementation by Specialist Agent (with Ollama briefing for L1+; typically medium/high effort after low-effort intake)
- **validate**: Validation Agent checks syntax, imports, patterns
- **review**: Create review document, activate Critic for L3+
- **docs**: Documentation Agent updates Docs/ and MEMORY.md
- **archive**: Record decision in `.claude/knowledge/decisions.md`; for completed plan, execute **task archival (BP-005)** → see `governance/task_archival.md`

> All Docs paths are relative to `.project/`. Example: `Docs/Plans/` → `.project/Docs/Plans/`.

**Minimal context principle:** Each agent receives only what they need. Librarian builds context packs.

---

## Step 5 — Ollama Gate (For L1+)

```python
from src.ollama_client import OllamaClient, OllamaUnavailableError

client = OllamaClient()
if level >= 1 and not client.is_available():
    raise OllamaUnavailableError("Ollama not reachable — FREEZE")
```

→ If unavailable: **FREEZE** — no partial implementation without briefing.
→ Full protocol: `governance/ollama_integration.md § Freeze Protocol`

---

## Step 6 — After Each Step

- **Smoke check** execute: `python3 src/main.py --task "test ollama"` (for code changes)
- **Update docs** when behavior changed (CLAUDE.md, agent definitions)
- **Log significant decisions** in `.claude/knowledge/decisions.md`

---

## Step 7 — Shell / Patch Application

- **Manual-only by default.** No shell commands or patches without explicit user approval.
- Exception: Bash tool permissions in `settings.local.json` (only commands listed there).

---

## Step 8 — Document Completion

Every task ends with:
1. Set plan status to `IMPLEMENTED` or `CLOSED`
2. Document deviations from plan (inline in plan document)
3. Update MEMORY.md (if stable new insight)
4. Update Decisions.md (if architecture or policy decision)
5. **Archival (BP-005):** Mark task as done in task list; for completed plan, trigger agent system for archival (results → `Docs/References/`, `Docs/Documentation/`, `.claude/knowledge/index.md`) — full protocol: `governance/task_archival.md`
