# MVP workflow rule (ClaudeClockwork)

**Applies to:** ClaudeClockwork MVPs only (CCW-MVP01 onward). This chain is not for LlamaCode; LlamaCode has its own framework and roadmap.

---

## Rule

**Single canonical MVP list:** `.claude-development/Clockwork_MVP_Chain.md`

Put every new MVP definition (Goal, Deliverables, Acceptance) **in this file** — not in separate files.

---

## Do / Do not

| Action | Do | Do not |
|--------|-----|--------|
| Define new MVP | Append a section to `Clockwork_MVP_Chain.md` (same format as CCW-MVPnn) | Create a new file e.g. `MVP_25_xyz.md` |
| Follow-up to MVP | Extend the existing section in the chain or add a new CCW-MVPnn section after it | Create a separate "MVP follow-up" document elsewhere |
| Design before implementation | Add design MVP (e.g. MVP22-D) as a section in the chain; reference design outputs in `designs/` | Describe the MVP only in another file without a chain entry |
| Milestone plan (M1, M2, …) | Store plan in `milestones/`; plan references MVP IDs from the chain; chain holds the actual MVP text | Keep MVP text only in the milestone plan, not in the chain |

---

## Supporting artifacts (allowed)

- **milestones/** — Milestone plans. They list MVP IDs and order; the chain holds the definitions.
- **designs/** — ADRs, specs, diagrams. Reference from the chain (e.g. "Design outputs: see designs/adr_runtime_critics_integration.md").
- **audits/** — Parity matrices, audit logs, completion logs. Reference from chain or milestone plan.

These **supplement** the chain; they do not replace it.

---

## Why

- One readable file with the full MVP sequence.
- No scattered definitions — open the chain to see any MVP.
- Single source of truth for humans and agents.
