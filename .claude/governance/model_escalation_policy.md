# Model & Agent Escalation Policy

**Goal:** Token/cost reduction with consistent quality through *small-first* routing, controlled escalation, and a fixed 3-level agent hierarchy.

This policy is the canonical reference for:

- **Control #1:** Higher/different **local Oodle model**
- **Control #2:** Higher **Claude model**

---

## 1) Agent Hierarchy (3 Levels)

### Orchestrator (Control Plane)
- Intake → Routing → Budget → Dispatch → Merge → Gates → Archive
- Does **no** deep implementation

### SpecialAgents (Departments)
- Deliver capabilities, build packs, normalize results
- Work with **small context**

### Worker (Execution Plane)
- Write code/reports, triage tests, fix bugs
- Receive **Pack + TasklistSpec** (not the entire original conversation)

---

## 2) Trust Modes (Control Context Costs)

Every handoff carries a trust mode:

- `inherit`: Worker trusts **TasklistSpec + Pack** (no full read)
- `verify`: Worker additionally receives **Goal/Constraints Extract** (10–20 lines)
- `rebuild`: Worker ignores TasklistSpec and builds plan anew (expensive)

**Default:** `inherit`.
`rebuild` only for `risk=high` or `confidence < 0.5`.

---

## 3) Contracts (Utility)

Contracts only seem "weird" if you view them as overhead. In agent teams, they are the **context saver**:

- **Deterministic**: Merger/Gates can decide mechanically
- **Routable**: Personaler can route on fields (risk/confidence/errors)
- **Learnable**: Quality tracking per model/agent/task becomes stable

Free text is allowed in `notes`/`rationale`, but not as a substitute for core fields.

---

## 4) Escalation Ladder (Oodle → Claude)

### 4.1 Oodle Model Tiers (Local)

- **Tier S (small):** 7b–14b (Routing, Packing, Admin, quick reviews)
- **Tier M (medium):** 32b–33b (Implementation, concrete fixes)
- **Tier L (large):** 70b–72b (hard reasoning, multi-module triage)

### 4.2 Claude Tiers (Cloud)

- **Claude S:** Haiku (administrative, dispatch, light reviews)
- **Claude M:** Sonnet (Plan/Review/Debug medium)
- **Claude L:** Highest available reasoning (gate-driven only)

### 4.3 Rule: Oodle First, Then Claude

When a result is insufficient, escalate in this order:

1) **Oodle**: S → M → L (or switch model family, e.g., qwen → llama)
2) **Claude**: Haiku → Sonnet → Higher

---

## 5) Critic Feedback Loop for the Personaler

The Personaler should get signal **between** runs on whether their routing was good.
This happens via the **Report Worker**, which evaluates error/quality density.

### 5.1 Report Worker Delivers `QualitySignal`

- `error_count` (hard errors)
- `warning_count`
- `recurrence` (same errors repeated?)
- `confidence_drop` (e.g., reviewer uncertain)
- `recommend_escalation` (none|oodle|claude)

### 5.2 Thresholds (Default)

- **Escalate Oodle** when:
  - `error_count >= 3` **or**
  - `recurrence >= 2` **or**
  - `confidence_drop` strong

- **Escalate Claude** when:
  - Oodle Tier L already used and still `error_count >= 2`
  - or `risk=high` gate triggers

### 5.3 Critic as Corrective

When Report Worker delivers `recommend_escalation != none`, the Personaler must:

1) Request critic report (technical/systemic) **or** read existing one
2) Adjust routing decision
3) Justify the change in routing dict (`rationale`)

---

## 6) TestOps Special Rule (Free → More Runs OK)

Tests are executed deterministically. LLMs only triage logs and create fix plans.

- Escalate Light → Medium → Heavy (locally)
- Only escalate to Claude on repeated failure

---

## 7) Claude Tier Policy (Full Bandwidth, Cost-Aware)

**Principle:** *Small-first*, then secure via independent verification. Escalation happens **first via Oodle**, only then via Claude.

### Claude Tiers (Cloud)

- **C0 — Low-Level / Cheap:** Claude **4** / **4.1**
  - Admin/Dispatch, checklists, "dumb" tasklist execution, simple format/refactor routines (when guided via packs).
- **C1 — Fast:** Claude **4.5 Haiku**
  - Task compaction, quick reviews, short queries, "what's broken?" triaging.
- **C2 — Precise:** Claude **4.5 Sonnet**
  - Precise implementation/reviews, diff-based corrections, difficult bugfixes.
- **C3 — Critical Gate (sparse):** Claude **4.6 Sonnet**
  - Only for *decisive* points: high-risk fix, final architecture decision, "last resort" debug.
- **C4 — Disabled by default:** **Opus 4.6**
  - Too expensive → manual only, outside normal automations.

### Escalation Rule (Claude)

1. **C0 → C1** when output unclear/inconsistent, but risk is low.
2. **C1 → C2** when precise engineering work is needed (code/design quality).
3. **C2 → C3** only when: repeated failure, high-risk, security/determinism/governance gate.
4. **C4** manual only.

---

## 8) Pattern: Cheap Doer + Independent Verifier

When a cheap agent (C0/C1 or O0/O1) only "executes", an independent verifier **must** check:

- **Doer:** Executes TasklistSpec, creates diff/artifacts
- **Verifier:** Checks diff/tests/logs (O2/O3 or C2)
- **Governor:** Decides Accept/Retry/Escalate (Critic / Governance Gate)

This pattern saves context because the doer doesn't "think", but works — and quality is still ensured.
