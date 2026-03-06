# Decisions Log — Python Orchestrator

> Append-only. Short, dated entries. Long-term reference for architecture and policy decisions.
> Owner: Team Lead (via file_ownership.md)

---

## Template

```
- Date:        YYYY-MM-DD
- Decision:    [What was decided]
- Context:     [Why was the decision necessary]
- Options:     [At least 2 alternatives]
- Rationale:   [Why this option]
- Follow-ups:  [Consequences, next steps]
```

---

## 2026-02-27 — Migration from WarCollection UE5 to Python Orchestrator

- Date: 2026-02-27
- Decision: Complete migration of the `.claude/` system from a UE5 game project to the Python Orchestrator.
- Context: The previous system was oriented toward Unreal Engine (`.claude/unreal/`). The new project is a Python console application for autonomous Ollama/Claude agent orchestration.
- Options: (A) Adapt existing system, (B) Complete recreation of `.claude/` governance.
- Rationale: Option B — too much UE5-specific logic that is not transferable.
- Follow-ups: Built `src/` directory (main, orchestrator, workflow, ollama_client, claude_client, config, agents/).

---

## 2026-02-27 — stdlib-only as Constraint

- Date: 2026-02-27
- Decision: No external Python dependencies. Only Python stdlib.
- Context: Easy installability, no virtualenv overhead, maximum portability.
- Options: (A) requests + pydantic, (B) stdlib only (urllib, subprocess, json, pathlib).
- Rationale: Option B — the overhead of external packages outweighs the benefit for this use case.
- Follow-ups: requirements.txt documents stdlib-only. For L2 escalation, involve Architecture Agent if external packages are needed.

---

## 2026-02-27 — Oodle Concepts Adopted in Python Orchestrator

- Date: 2026-02-27
- Decision: Selective adoption of Llama Code (formerly Oodle Code) CMD concepts into .claude/ governance.
- Context: OODLE.md / `.claude/` system contains mature concepts for routing, context budget, quality tracking.
- Adopted: decisions.md pattern, execution phases (intake|plan|build|validate|review|docs|archive), L5 gate trigger list, minimal context principle.
- Not adopted: YAML runtime storage (.llama_runtime/writes/), external provider management, full enterprise agent tree.
- Rationale: Python Orchestrator is Ollama-first/local-first. Oodle runtime infra too complex for current scope.
- Follow-ups: Plan YAML-driven routing in orchestrator._classify() as L2 task.
