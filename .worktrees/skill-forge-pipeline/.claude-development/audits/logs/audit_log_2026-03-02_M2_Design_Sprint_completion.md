# M2 Week 2 — P0 Design Sprint Completion (MVP22-D, MVP23-D, MVP24-D)

**Date:** 2026-03-02  
**Plan:** `.claude-development/milestones/M2_clockwork_audit_followup_plan_2026-03-02.md`  
**Scope:** Design MVPs (Do First) — P0 only

---

## MVP22-D — Runtime Critics Architecture

| Deliverable | Location |
|-------------|----------|
| ADR: Runtime Critics Integration | `.claude-development/designs/adr_runtime_critics_integration.md` |
| CriticResult JSON schema | `.claude/contracts/schemas/critic_result.schema.json` |
| critic_gates.yaml spec | `.claude-development/designs/critic_gates_spec.yaml` |
| Critic–pipeline interface diagram | In ADR (ASCII) |

---

## MVP23-D — Capability Policy Design

| Deliverable | Location |
|-------------|----------|
| capabilities.yaml (full spec) | `.claude-development/designs/capabilities_spec.yaml` |
| command_allowlist.yaml spec | `.claude-development/designs/command_allowlist_spec.yaml` |
| Per-agent capability matrix | `.claude-development/designs/per_agent_capability_matrix.md` |
| Enforcement mechanism ADR | `.claude-development/designs/adr_capability_enforcement.md` |

---

## MVP24-D — Eval Harness Completion Design

| Deliverable | Location |
|-------------|----------|
| task_suite.yaml | `.claude/eval/task_suite.yaml` (core, stress, exploration) |
| schedules.yaml | `.claude/eval/schedules.yaml` (nightly, weekly_power, pre_release, shadow) |
| shadow/ and ab/ directory specs | `.claude-development/designs/eval_shadow_ab_cbl_spec.md` |
| CBL rung benchmark task definitions | `.claude/eval/cbl/` (unlock_rules.yaml, rung_1 example, README) |

---

## Next (per plan)

- **Week 3:** MVP23 (Runtime Critics v1 — Drift + Regression), MVP24 (Capability Policy Enforcement), MVP25 (Eval Harness Completion).
- Implementation consumes these design artifacts; no implementation code in this sprint.
