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

Full detail: `.claude-development/MVP_RULE.md` and `.claude-development/README.md`.

## Why

- One readable, complete MVP list.
- No scattered definitions.
- Single source of truth: "What is MVP X?" → open the chain.
