# B-013 — Adaptive Router v1 Design (M1 Design-Only)

**Date:** 2026-03-02  
**Status:** Design; implementation deferred to M2  
**Scope:** Bandit-based model/tier selection using outcome ledger

---

## Goal

Define an **adaptive router v1** that consumes the outcome ledger (and optionally route_profiles) to recommend or select model/tier for the next task, using a **bandit algorithm** so that over time the system explores and exploits the best-performing arms (model/tier combinations).

---

## 1) Prerequisites (Must Be Done Before Implementation)

- **B-001–B-004:** All mutable state (outcome_ledger, route_profiles, brain) must live under `.llama_runtime/`. No references to `.claude/knowledge/` for these. (Done in M1.)
- **Ledger format:** Outcome events in `.llama_runtime/knowledge/outcome_ledger.jsonl` (or `.llama_runtime/outcome_ledger/quality_signals.jsonl`) with at least: `task_type`, `model`, `tier`, `outcome` (pass/fail), optional `latency_ms`, `critic_score`.

---

## 2) Bandit Algorithm Spec (v1)

**Model:** Contextual multi-armed bandit (simplified).
- **Arms:** (tier, model) pairs from palette (e.g. S/7b, M/14b, L/70b).
- **Context:** Task tags or task_type (e.g. "plan_lint", "code_clean", "qa_gate").
- **Reward:** Binary or scalar from outcome (e.g. 1 if pass, 0 if fail; or critic_score normalized to [0,1]).

**Update rule:**
- After each run: append outcome to ledger; optionally update internal counts (e.g. per-arm success/fail counts per context).
- Selection rule: **UCB1** or **epsilon-greedy** over arms available for the context. Prefer simplicity: epsilon-greedy with epsilon=0.1 (10% random exploration, 90% best arm so far).

**Constraints:**
- Only recommend from palette; never recommend a model not in `.oodle/models/palette.yaml` or equivalent.
- Hardware and policy constraints (e.g. GPU-only for certain models) must be respected before bandit choice.

---

## 3) Interfaces

**Input (for M2 implementation):**
- `task_context`: dict with task_type, optional tags.
- `available_arms`: list of (tier, model) from palette filtered by hardware/policy.

**Output:**
- `recommended_tier`, `recommended_model`, `rationale` (e.g. "best pass rate in last 30 runs for this task_type").

**Storage:**
- Read: `.llama_runtime/knowledge/outcome_ledger.jsonl` (or quality_signals.jsonl).
- Optional: aggregated stats in `.llama_runtime/brain/` (e.g. model_routing_stats.json) to avoid re-reading full ledger every time.

---

## 4) Relationship to Existing Code

- `llamacode/core/bandit_router.py` exists (referenced in backlog). Design should align with its intended API: e.g. `select(task_context, available_arms) -> (tier, model)`.
- `route_autotune_suggest` skill already suggests tweaks from ledger; adaptive router is the consumer that applies selection at runtime.

---

## 5) Non-Goals (M1)

- No implementation in bandit_router.py or new module.
- No integration with Personaler or CLI.
- No A/B testing or shadow mode in M1.

End.
