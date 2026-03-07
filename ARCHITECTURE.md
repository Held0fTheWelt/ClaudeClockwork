# Project Architecture

**Canonical overview.** For detailed knowledge architecture see `.claude/knowledge/architecture.md` and `.claude/python/architecture.md`.

## Overview

Clockwork is a meta-governance system for multi-agent Claude/Ollama orchestration.

- **System files:** `.claude/` — agents, governance, contracts, skills, tools, knowledge
- **Project files:** `.project/` — memory, docs, roadmap, quality tracking (this project)
- **Deployment:** when used on another project, `.project/` contents move to that project's root

## Key Design Principles

- Local-model-first (Ollama) — escalate to Claude only when needed
- Small-first model selection — escalate tier before switching providers
- Strict file ownership — no agent edits outside its domain
- Contracts over freitext — all inter-agent data uses typed JSON specs

## Primary Package

- **`claudeclockwork/`** — main runtime package (v0.1.0). Core modules: CLI, runtime factory, legacy bridge, executor pipeline, skill registry, capability planner, permission security.

> Note: `llamacode/`, `oodle/`, and `src/` referenced in older docs no longer exist. `claudeclockwork/` is the canonical package.

## Runtime Layout

| Area | Location |
|------|----------|
| Clockwork (agents, skills, governance) | `.claude/` |
| Runtime state (ledgers, eval results, writes) | `.clockwork_runtime/` (created; `eval/results/` pre-seeded) |
| Reports | `.report/` |
| Telemetry | `.claude-performance/` |

## Key Subsystems

- **Routing:** `claudeclockwork/core/planner/` + `core/security/`; model routing config in `.claude/config/model_routing.yaml`.
- **Skills:** `.claude/tools/skills/` (94 legacy Python modules); manifest-based skills in `.claude/skills/` (34 skills, 30 via legacy adapter).
- **Registry:** `claudeclockwork/core/registry/` — discovers `manifest.json` files, loads via importlib.
- **Eval:** `.claude/eval/eval_runner.py`; results → `.clockwork_runtime/eval/results/`.
