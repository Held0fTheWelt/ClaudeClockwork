# Memory Index — WorldOfShadows

Persistent knowledge across sessions. Load this first at session start.

## Project Context
- [PROJECT_CONTEXT.md](../.clockwork_runtime/knowledge/PROJECT_CONTEXT.md) — Identity, tech stack, current initiatives, implementation details, code patterns

## Agent Infrastructure
- [ROLES.md](./agents/ROLES.md) — Agent role definitions, dispatch pattern, evidence trail
- [.llama_runtime/README.md](../.llama_runtime/README.md) — Ollama model assignments, execution protocol
- [.clockwork_runtime/README.md](../.clockwork_runtime/README.md) — Runtime structure for phase orchestration

## Phase Results (Narrow Task.md)

### Completed Phases
- Phase 1: Delta scope frozen — commit 2ad5a92
- Phase 2: News auto-suggestions — commit db282ef
- Phase 3: Wiki auto-suggestions — commit 2206ae0
- Phase 4: Contextual enrichment — commit 2206ae0
- Phase 5: Tests (6 passing) — commit 5f4d7f2
- Phase 6: Postman/docs/changelog — commit e75b929

See `.clockwork_runtime/reports/` for detailed gate reports.

## For Future Work

1. **Check cache first:** `.clockwork_runtime/workgraph_cache/<phase_name>/`
2. **Read gate reports:** `.clockwork_runtime/reports/`
3. **Access agent brain:** `.clockwork_runtime/brain/` for state/decisions
4. **Update this file** when new learnings emerge

## Session Checkpoints

- Session 1: Implemented Phases 1-6 of narrow Task.md
- Session 2: Set up full Clockwork infrastructure (this session)
- Status: Ready for future pure-Ollama hybrid agent orchestration
