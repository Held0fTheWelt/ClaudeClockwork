# MVP development standard (ClaudeClockwork)

**Applies to:** ClaudeClockwork MVPs only (CCW-MVP01 onward). Do not add LlamaCode framework MVPs to the Clockwork chain; LlamaCode is a separate framework.

## Canonical location

- **MVP list (single file):** `.claude-development/Clockwork_MVP_Chain.md`
- **Supporting artifacts:** `.claude-development/milestones/`, `.claude-development/designs/`, `.claude-development/audits/`

## Rules

1. **New MVP definitions** (Goal, Deliverables, Acceptance) go **only** in `.claude-development/Clockwork_MVP_Chain.md` — not in separate files.
2. **Follow-ups and extensions** — add a new CCW-MVPnn section in the chain or extend the existing section.
3. **Milestone plans** (M1, M2, …) live in `.claude-development/milestones/` and reference MVP IDs from the chain; definitions stay in the chain.
4. **Design outputs** (ADRs, specs) live in `.claude-development/designs/` and are referenced from the chain by MVP-ID.

Full detail: `.claude-development/MVP_RULE.md` and `.claude-development/README.md` (both now read-only historical references — this file is the canonical standard).

<!-- Merged from .claude-development/MVP_RULE.md (Phase 11) -->

## Do / Do not

| Action | Do | Do not |
|--------|-----|--------|
| Define new MVP | Append a section to `Clockwork_MVP_Chain.md` (same format as CCW-MVPnn) | Create a new file e.g. `MVP_25_xyz.md` |
| Follow-up to MVP | Extend the existing section in the chain or add a new CCW-MVPnn section after it | Create a separate "MVP follow-up" document elsewhere |
| Design before implementation | Add design MVP (e.g. MVP22-D) as a section in the chain; reference design outputs in `designs/` | Describe the MVP only in another file without a chain entry |
| Milestone plan (M1, M2, …) | Store plan in `milestones/`; plan references MVP IDs from the chain; chain holds the actual MVP text | Keep MVP text only in the milestone plan, not in the chain |

## Supporting artifacts (allowed)

- **milestones/** — Milestone plans. They list MVP IDs and order; the chain holds the definitions.
- **designs/** — ADRs, specs, diagrams. Reference from the chain (e.g. "Design outputs: see designs/adr_runtime_critics_integration.md").
- **audits/** — Parity matrices, audit logs, completion logs. Reference from chain or milestone plan.

These supplement the chain; they do not replace it.

## Why

- One readable, complete MVP list.
- No scattered definitions.
- Single source of truth: "What is MVP X?" → open the chain.

---

## Phase MVP files (`mvps/`)

Phase specs (e.g. `mvps/MVP_Phase44_StablePublicSurface.md`) use a **Definition of Done** section. When a DoD item is implemented, mark it with `- [x]`; unimplemented items stay `- [ ]`. **Template:** the DoD section must look exactly like in `mvps/MVP_Phase30_WorkGraphEngine.md` and `mvps/MVP_Phase31_LearningLayer.md` (plain list, same layout). Apply when implementing or closing any phase. See `.project/MEMORY.md` (User Preferences).
