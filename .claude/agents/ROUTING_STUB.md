# Routing Stub (CCW-MVP03)

_Derived from: `.claude/governance/routing_matrix.md` and `model_escalation_policy.md`_
_Full routing details live in those canonical files — this stub is a quick-reference summary._

---

## Decision Tree

```
Incoming task
  │
  ├─ Trivial / single-file / no Ollama needed?
  │    └─► L0 — Worker direct (TeamLead handles inline, no Personaler)
  │         Output: edited file + inline note
  │
  ├─ Multi-file, clear scope, standard implementation?
  │    └─► L1 — TeamLead routes via Personaler → Implementation Worker
  │         Output: JSON {status, changed_files, notes, rerun_tests}
  │
  ├─ Cross-module, API surface, or architecture decision?
  │    └─► L2 — Architecture Agent + Designer review before Worker
  │         Output: Markdown architecture proposal → approved → Worker JSON
  │
  ├─ Performance-critical / data persistence / network replication / security?
  │    └─► L3 — Critic-Technical mandatory (+ optional Critic-Systemic)
  │         Output: Markdown Audit (APPROVE / APPROVE WITH CONDITIONS / REWORK)
  │
  ├─ External provider call / new agent type / governance rule change?
  │    └─► L4 — Critic-Systemic mandatory + Personaler escalation gate
  │         Output: Markdown Systemic Audit + updated RoutingSpec
  │
  └─ Publish / delete / breaking change / L5 threshold?
       └─► L5 — STOP. User confirmation required before any action.
            Output: confirmation prompt; no automated writes
```

---

## Output Format Per Level

| Level | Who Acts | Output Format | Destination |
|---|---|---|---|
| L0 | TeamLead (inline) | none / inline edit | file in place |
| L1 | Implementation Worker | JSON result | returned to TeamLead |
| L2 | Architecture Agent | Markdown proposal | `Docs/Plans/` |
| L3 | Critic-Technical | Markdown audit | `Docs/Audits/` |
| L4 | Critic-Systemic | Markdown audit | `Docs/Audits/` |
| L5 | (blocked) | user prompt | n/a |

---

## Escalation Ladder (cost control)

1. Oodle local: Tier S (7b–14b) → Tier M (32b–33b) → Tier L (70b–72b)
2. Claude cloud: Haiku (C1) → Sonnet (C2/C3) → Opus (C4, manual only)

Rule: exhaust Oodle tiers before escalating to Claude.

---

## Routing Source of Truth

- Full matrix: `.claude/governance/routing_matrix.md`
- Escalation thresholds: `.claude/governance/model_escalation_policy.md`
- Level definitions: `.claude/governance/escalation_matrix.md`
- Department/capability mapping: `.claude/agents/personaler.md` § Routing-Regeln
