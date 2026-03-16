# ClaudeClockwork Legacy Development Archive

> **ARCHIVED — Read-only as of Clockwork v18.**
> This directory contains historical development artifacts for Clockwork up to and including v17.x.
> Do not add new content here.
>
> Active locations:
> - MVP plans → `mvps/`
> - Roadmaps → `roadmaps/`
> - Design decisions → `.claude/knowledge/`
> - Governance standards → `.claude/governance/`

---

# Clockwork Development (.claude-development)

**Canonical location for all ClaudeClockwork MVPs and development artifacts.**

This folder is **ClaudeClockwork only**. LlamaCode is a separate framework with its own roadmap and MVP list; do not add LlamaCode MVPs or framework deliverables here.

---

## Start here: single MVP list

| Document | Content |
|----------|--------|
| **[Clockwork_MVP_Chain.md](Clockwork_MVP_Chain.md)** | **Chronological MVP archive + full definitions.** At the top: one table of all MVPs in delivery order (ID, name, status, date/milestone) so you can trace history. Below: full Goal/Deliverables/Acceptance for each MVP in the same file. MVP01–MVP33 and design MVPs; no need to look elsewhere for the list. Do not split MVP definitions across other files. |

---

## Folder structure

```
.claude-development/
├── README.md                 ← you are here
├── MVP_RULE.md               ← rule: new MVPs only in the chain
├── Clockwork_MVP_Chain.md    ← CANONICAL MVP LIST (single source of truth)
├── milestones/               ← milestone plans (M1, M2, …); reference MVP IDs from the chain
├── designs/                  ← design outputs (ADRs, specs) for design MVPs
└── audits/                   ← parity/, logs/; completion logs and audit cadence
```

- **milestones/** — Plans (e.g. M1_parity_followup_plan, M2_clockwork_audit_followup_plan). They reference MVP IDs; full MVP text is in `Clockwork_MVP_Chain.md`.
- **designs/** — ADRs, spec YAMLs (e.g. Runtime Critics, Capability Policy, Eval Harness). Reference by MVP-ID (e.g. MVP22-D).
- **audits/** — parity/, logs/. Completion logs (e.g. M1 completion, M2 MVP22 completion) and audit cadence.

---

## Rule: MVP workflow

**Add new MVPs and follow-ups only to the canonical MVP list.**

- **Do not:** Create separate MVP definition files (e.g. `MVP_25_xyz.md`).
- **Do:** Append or insert entries in **Clockwork_MVP_Chain.md** using the same format as existing CCW-MVPnn sections.
- Supporting artifacts (design doc, milestone plan, audit log) may live in `milestones/`, `designs/`, `audits/` but must reference the MVP ID in the chain. The **definition** (Goal, Deliverables, Acceptance) lives only in the chain.

Details: [MVP_RULE.md](MVP_RULE.md)
