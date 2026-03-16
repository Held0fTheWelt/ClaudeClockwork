# Agent Routing Intelligence

> Grows over time through experiences of all agents. Used by Team Lead for agent and model selection.
> Entries are added after completed tasks.

---

## Composition Principle

Agent roles are guidance. Team Lead selects the smallest, most precise team per task:
- L0: 1 Specialist (haiku) — no QA needed
- L1: 1 Specialist (sonnet) + Collector if risk present
- L2+: Specialist + Validation + possibly Critic
- No agent is added for completeness — only with real benefit

---

## Task → Agent + Model Mapping

| Task Type | Agent | Model | Ollama Type | Prerequisites |
|---|---|---|---|---|
| New Python function/class (complete) | Implementation Agent | sonnet | `draft` | Ollama draft as basis |
| Single-file bugfix (Python) | Implementation Agent | haiku | `quick` or none (L0) | — |
| Ollama client change | Implementation Agent | sonnet | `draft` | Inject architecture.md |
| New top-level module in `src/` | Architecture Agent | sonnet | `architecture` | Architecture Review L2 |
| Technical documentation | Documentation Agent | haiku | `brief` | Source code read first |
| Index/archive knowledge | Librarian Agent | haiku | — | Completed implementation as input |
| Correctness against acceptance criteria | Collector Agent | haiku | — | Task Brief with criteria present |
| Syntax / import / runtime validation | Validation Agent | sonnet | `review` | Code complete |
| Pattern extraction | Pattern Recognition Agent | sonnet | — | Min. 2 similar implementations |
| Architecture decision | Architecture Agent | sonnet | `architecture` | L2 escalation |
| L3 performance / subprocess pooling | Technical Critic | sonnet | `architecture` | Validation report present |
| Write/update governance docs | Implementation Agent | sonnet | — | Clear content plan present |
| Status checks (test ollama) | — | haiku | — | Only script execution needed |
| Efficiency analysis / routing advice | Skill Agent | sonnet | `architecture` (phi4:14b) or `brief` (qwen2.5-coder:14b) | Recent tasks as observation basis |

---

## Known Routing Anti-Patterns

- **Implementation Agent for architecture decisions** → wrong: Architecture Agent
- **Haiku for new Python class** → too weak for complex implementation: sonnet + Ollama draft
- **Specialist without Ollama briefing for L1+** → forbidden per execution_protocol.md
- **Documentation Agent without source code basis** → docs become inaccurate

---

## Domain Context Injection Table

| Domain Detection Feature | Context File | Agent |
|---|---|---|
| `OllamaClient`, `ollama_client`, Ollama HTTP | `<PROJECT_ROOT>/src/ollama_client.py` | Implementation Agent |
| `ClaudeClient`, `claude_client`, subprocess spawn | `<PROJECT_ROOT>/src/claude_client.py` | Implementation Agent |
| `Orchestrator`, `workflow`, trigger recognition | `<PROJECT_ROOT>/src/orchestrator.py` | Implementation Agent |
| `config.DOCS_PATH`, `config.CLAUDE_PATH` | `<PROJECT_ROOT>/src/config.py` | Implementation Agent |
| `BaseAgent`, `AgentResult`, `<PROJECT_ROOT>/src/agents/` | `<PROJECT_ROOT>/src/agents/base.py` | Implementation Agent |
| Module boundary, dependency direction | `.claude/python/architecture.md` | Architecture Agent |
| Python patterns (Freeze, Spawn, Output) | `.claude/python/patterns.md` | Implementation Agent |

---

## Routing Calibration (Grows Over Time)

| Date | Task Type | Chosen Agent+Model | Result | Note |
|---|---|---|---|---|
| 2026-02-26 | Create governance docs (Learning System) | Implementation Agent + sonnet | Good | Content fully pre-planned → Agent only executing |
| 2026-02-26 | Status check (test ollama) | — haiku | Good | Simple script execution, no reasoning needed |
| 2026-02-27 | Python Orchestrator migration (complete) | Claude Code direct | Good | Complex multifile migration, no subagent overhead needed |


## operations.observability
- Department Lead Ops Ledger (silent): `.claude/agents/operations/department_lead_ops_ledger.md`
