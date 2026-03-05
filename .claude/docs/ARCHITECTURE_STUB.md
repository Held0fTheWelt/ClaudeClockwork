# Architecture Overview — OllamaCode / LlamaCode

_Last updated: 2026-03-02 (CCW-MVP04) — fill-in stub_

## Project identity

| Field            | Value                                      |
|------------------|--------------------------------------------|
| Project          | OllamaCode / LlamaCode                     |
| Version          | v6.5.0-MVP9                                |
| Primary package  | `llamacode/`                               |
| Entry point      | `llamacode/cli.py` (Click group `oodle`)   |
| Clockwork        | `.claude/` (methodology only — read-only)  |
| Runtime root     | `.llama_runtime/`                          |
| Docs root        | `docs/`                                    |
| Plugin folder    | `plugins/`                                 |

## Key modules

| Module                      | Purpose                                                  |
|-----------------------------|----------------------------------------------------------|
| `llamacode/cli.py`          | CLI entry point; registers all command groups            |
| `llamacode/core/runner.py`  | `TaskRunner` — executes a `Task` JSON file               |
| `llamacode/core/planner.py` | `DeterministicPlanner` — converts `TaskSpec` → `Plan`   |
| `llamacode/core/plan_executor.py` | `PlanExecutor` — runs a `Plan` step-by-step        |
| `llamacode/core/snapshot.py`| `SnapshotStore` — point-in-time workspace capture        |
| `llamacode/core/audit_log.py` | Append-only operation audit trail                      |
| `llamacode/schemas/`        | Pydantic schemas: `Task`, `TaskSpec`, `Plan`, `Pack`, etc|
| `llamacode/providers/`      | Provider abstraction (Ollama default; opt-in externals)  |
| `llamacode/plugins/`        | Plugin discovery, manifests, enable/disable state        |
| `llamacode/core/intent_router.py` | Maps `TaskSpec` to agent/team                    |
| `llamacode/core/message_bus.py`   | Inter-agent communication channel                  |
| `llamacode/core/budget_monitor.py`| Token/compute budget enforcement per agent         |

## Directory layout (top-level)

```
llamacode/          Primary package (CLI + core + schemas + providers + plugins)
docs/               User-facing documentation (DO NOT modify from clockwork)
.claude/            Clockwork — methodology, skills, agents, governance (read-only)
.llama/             Llama-branch clockwork (absent on claude branch)
.llama_runtime/     Runtime state — snapshots, audit, artifacts (never committed)
plugins/            Extension modules
quellen/            Reference sources / legacy read-only archive
scripts/            Repo tooling scripts
tests/              Automated test suite
```

## Data-flow summary

```
User → oodle CLI → TaskSpec/Task JSON
  → DeterministicPlanner → Plan
  → PlanExecutor (+ SnapshotStore + AuditLog)
  → Providers (Ollama / opt-in external)
  → TaskReport → .llama_runtime/
```

## Further reading

- Full architecture doc: `docs/tech/architecture.md`
- System map diagram: `docs/diagrams/system_map.md`
- CLI reference: `docs/tech/api_or_cli.md`
