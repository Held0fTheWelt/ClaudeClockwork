# Project Architecture (Root)

**Canonical overview.** For detailed knowledge architecture see `.claude/knowledge/architecture.md` and `.claude/python/architecture.md`.

## Primary Package

- **`llamacode/`** — main runtime package (v6.5.0-MVP9+). Core modules: routing, plan execution, bandit router, escalation, skills, CLI.
- **`oodle/`** — legacy/reference package (parallel structure); may be archived per roadmap.
- **`src/`** — legacy stubs; product code origin policy: see `.claude/policies/SRC_ORIGIN_RULE.md`.

## Runtime Layout

| Area | Location |
|------|----------|
| Clockwork (agents, skills, governance) | `.claude/` |
| Runtime state (ledgers, eval results, writes) | `.llama_runtime/` |
| Reports | `.report/` |
| Telemetry | `.claude-performance/` |

## Key Subsystems

- **Routing:** `llamacode/core/bandit_router.py`, `escalation_router.py`; config in `.claude/config/model_routing.yaml`.
- **Skills:** `.claude/tools/skills/` (Python); definitions in `.claude/skills/`.
- **Eval:** `.claude/eval/eval_runner.py`; results → `.llama_runtime/eval/results/`.
