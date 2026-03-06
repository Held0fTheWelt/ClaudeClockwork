# Project Architecture (Root)

**Canonical overview.** For detailed knowledge architecture see `.claude/knowledge/architecture.md` and `.claude/python/architecture.md`.

## Primary Package

- **`claudeclockwork/`** — main runtime package (v0.1.0). Core modules: CLI, runtime factory, legacy bridge, executor pipeline, skill registry, capability planner, permission security.

> Note: `llamacode/`, `oodle/`, and `src/` referenced in older docs no longer exist. `claudeclockwork/` is the canonical package.

## Runtime Layout

| Area | Location |
|------|----------|
| Clockwork (agents, skills, governance) | `.claude/` |
| Runtime state (ledgers, eval results, writes) | `.llama_runtime/` |
| Reports | `.report/` |
| Telemetry | `.claude-performance/` |

## Key Subsystems

- **Routing:** `claudeclockwork/core/planner/` + `core/security/`; model routing config in `.claude/config/model_routing.yaml`.
- **Skills:** `.claude/tools/skills/` (94 legacy Python modules); manifest-based skills in `.claude/skills/` (34 skills, 30 via legacy adapter).
- **Registry:** `claudeclockwork/core/registry/` — discovers `manifest.json` files, loads via importlib.
- **Eval:** `.claude/eval/eval_runner.py`; results → `.llama_runtime/eval/results/`.
