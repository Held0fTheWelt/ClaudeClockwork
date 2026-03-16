# B-010 — Runtime Critics Design (M1 Design-Only)

**Date:** 2026-03-02  
**Status:** Design; implementation deferred to M2  
**Scope:** Drift critic + regression critic (automated quality signals)

---

## Goal

Define two runtime critics that can run in CI or post-run to produce **automated quality signals** without requiring manual review. Implementation is **not** part of M1.

---

## 1) Drift Critic

**Purpose:** Detect when the repo or clockwork artifacts have drifted from a declared baseline (contracts, schemas, skill dispatch, pointer targets).

**Inputs:**
- Baseline snapshot or declared invariants (e.g. list of pointer files and their targets, skill_runner dispatch keys, schema IDs).
- Current repo state (same targets).

**Output:**
- Report: `drift_critic_report.json` with:
  - `pointer_drift`: list of pointer files whose targets no longer exist or changed.
  - `dispatch_drift`: skill IDs in registry or skill docs that are not in skill_runner SKILLS.
  - `schema_drift`: contract examples that no longer validate against their schemas.
- Exit code: 0 = no drift, 1 = drift detected (configurable as blocker or warning).

**Invocation (future):**
- From `scripts/gate.sh` or a dedicated step in `.github/workflows/gate.yml`.
- Optional: run after `qa_gate` with `write_report: true`; drift critic consumes qa_gate report and adds drift-specific checks.

**Non-goals for M1:** No Python implementation. Only this design doc.

---

## 2) Regression Critic

**Purpose:** Detect when a run (e.g. validation run, eval run) regresses vs. a previous run (e.g. pass rate dropped, new failures, latency increase).

**Inputs:**
- Previous run report (e.g. `validation_runs/<id>/results.json` or `eval/results/run_*.json`).
- Current run report (same structure).

**Output:**
- Report: `regression_critic_report.json` with:
  - `pass_rate_delta`: e.g. 0.95 → 0.88 (regression if below threshold).
  - `new_failures`: check_ids or test names that passed before and fail now.
  - `latency_delta`: optional; if both reports have timing, flag significant increase.
- Exit code: 0 = no regression, 1 = regression detected.

**Invocation (future):**
- Post-step after integration tests or eval runs; compare latest run to a stored baseline (e.g. last green run on main).

**Non-goals for M1:** No Python implementation. Only this design doc.

---

## 3) Integration with B-005 / B-011

- **B-005 (CI gate):** Future M2 can add a step "Run drift critic" and optionally "Run regression critic" (e.g. compare to baseline artifact).
- **B-011 (integration tests):** Regression critic can consume `pytest` results (e.g. JUnit XML or a small JSON summary) and compare to previous run.

---

## 4) Out of Scope (M1)

- Actual Python modules for drift_critic and regression_critic.
- Wiring into gate.yml or skill_runner.
- Baseline storage strategy (where to store "last green" run).

End.
