# MVP Phase 31 — Learning Layer (Router + Policy Training)

**Goal:** Make routing choices improve over time using measured outcomes and user feedback, while keeping guardrails and preventing regressions.

**Why now:** Router v3 (Phase 26) plus scoreboards (Phase 25) makes evidence-driven optimization possible.

---

## Definition of Done

- [x] A feedback capture mechanism exists (manual rating + reason codes)
- [x] Router profiles can be updated offline from historical runs
- [x] Training job produces a new profile snapshot deterministically
- [x] Guardrails prevent unsafe/banned choices regardless of training
- [x] Regression gates apply to trained profiles
- [x] All existing tests pass

---

## L31.1 — Feedback Schema + Capture

**Files:**
- `.claude/contracts/schemas/feedback_event.schema.json` (new)
- `claudeclockwork/router/feedback.py`
- `Docs/feedback.md` (new)

**Change:**
- Capture:
  - success/failure
  - quality rating
  - latency satisfaction
  - reason codes (wrong tool, wrong model, too slow, etc.)

**Acceptance:**
- Feedback events validate against schema and write to telemetry JSONL.

---

## L31.2 — Offline Trainer + Profile Snapshots

**Files:**
- `claudeclockwork/router/training/offline_trainer.py`
- `tests/test_offline_trainer.py`

**Change:**
- Read telemetry + feedback and update bandit priors / success estimates.
- Write a new profile snapshot with version and timestamp.

**Acceptance:**
- Deterministic seed yields reproducible snapshot in tests.

---

## L31.3 — Guardrails + Safety Constraints

**Files:**
- Capability policy (Phase 24)
- Router constraints module

**Change:**
- Ensure training cannot override:
  - banned capabilities
  - external runner restrictions
  - redaction policy

**Acceptance:**
- Attempted override is blocked.

---

## L31.4 — Eval + Regression on Trained Profiles

**Files:**
- Eval harness (Phase 25)
- Regression gate (Phase 25)

**Change:**
- Evaluate trained profile vs baseline.
- Block training output if regression thresholds exceeded.

**Acceptance:**
- A bad trained profile is rejected deterministically.

---
