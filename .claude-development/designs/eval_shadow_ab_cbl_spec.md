# Eval Harness: shadow/, ab/, and CBL Spec (MVP24-D)

**Date:** 2026-03-02  
**References:** Report 06 (Eval Harness), Report 08 (CBL + Shadow-Operator)

---

## 1. shadow/ directory spec

**Purpose:** Store shadow-run artifacts (candidate config executed on same inputs as production; outputs recorded, not applied). Comparator produces a report.

**Location options:**
- **A:** `.claude/eval/shadow/` — under clockwork (design-only; no runtime writes here per invariant).
- **B (recommended):** `.llama_runtime/shadow/` — runtime state; per Report 08 §4.

**Structure (`.llama_runtime/shadow/`):**

```
.llama_runtime/shadow/
├── runs/
│   ├── <run_id>/
│   │   ├── baseline/          # production config outputs
│   │   │   └── results.json
│   │   ├── candidate/         # experimental config outputs
│   │   │   └── results.json
│   │   └── comparison.json   # delta, pass/fail, recommendation
├── latest_comparison.md      # Human-readable latest run (from schedules.yaml reporting)
└── promotion_rules.yaml      # When to promote candidate to production (e.g. min_improvement, no_regression)
```

**Implementation (MVP25):** Scaffold `shadow/runs/`, `promotion_rules.yaml` stub; comparator script consumes baseline + candidate results, writes comparison.json and latest_comparison.md.

---

## 2. ab/ directory spec

**Purpose:** A/B tests — side-by-side comparison of two configurations (e.g. model A vs model B, or static router vs adaptive router). Unlike shadow, both runs may be "real" experiments; outcome is which arm won.

**Location:** `.llama_runtime/eval/ab/` (runtime; not under .claude).

**Structure:**

```
.llama_runtime/eval/ab/
├── experiments/
│   ├── <experiment_id>/
│   │   ├── arm_a/            # e.g. config A results
│   │   │   └── run_results.json
│   │   ├── arm_b/
│   │   │   └── run_results.json
│   │   ├── config.yaml       # arm names, task suite, budget
│   │   └── report.md         # winner, confidence, metrics
├── configs/                  # Named configs (optional)
│   ├── production.yaml
│   └── adaptive_v1.yaml
└── .gitkeep
```

**Implementation (MVP25):** Scaffold `ab/experiments/` and `ab/configs/`; report template; actual A/B runner in later MVP.

---

## 3. CBL rung benchmark task definitions

**Purpose:** Formal benchmark tasks that define unlock criteria for each CBL rung (Report 08). Running these in a ceremony validates progression.

**Location:** `.claude/eval/cbl/` (clockwork — task definitions are versioned with the repo).

**Structure (from Report 08):**

```
.claude/eval/cbl/
├── unlock_rules.yaml         # Progression requirements, ceremony steps, demotion rules
├── rung_0_bootstrap/
│   ├── bench_parse_taskspec.yaml
│   ├── bench_select_agent.yaml
│   └── bench_produce_report.yaml
├── rung_1_single_agent/
│   ├── bench_route_simple.yaml
│   ├── bench_plan_simple.yaml
│   ├── bench_execute_with_snapshot.yaml
│   ├── bench_rollback.yaml
│   └── bench_report_generation.yaml
├── rung_2_multi_agent/
│   ├── bench_coordination.yaml
│   ├── bench_handoff.yaml
│   └── bench_budget_tracking.yaml
├── rung_3_quality_gated/
│   ├── bench_critic_activation.yaml
│   ├── bench_drift_detection.yaml
│   └── bench_regression_catch.yaml
├── rung_4_adaptive/
│   ├── bench_routing_improvement.yaml
│   ├── bench_cost_reduction.yaml
│   └── bench_eval_nightly.yaml
└── ... (rung_5 through rung_8 per Report 08)
```

**Benchmark task format (per Report 08):**

```yaml
id: "cbl_<rung>_<name>"
rung: <0..8>
description: "…"
timeout_seconds: 30
max_tokens: 2000
input:
  type: "task_spec" | "plan_request" | …
  payload: { … }
assertions:
  - type: "agent_selected" | "escalation_level" | "plan_steps" | "token_budget" | …
    expected: "…"
    weight: <0..100>
scoring:
  pass_threshold: 70
  excellent_threshold: 90
```

**Implementation (MVP25):** Create `unlock_rules.yaml` (from Report 08 §2); create one example benchmark per rung (e.g. `rung_1_single_agent/bench_route_simple.yaml`) as template; document remaining files as stubs to be filled in MVP30 (CBL Rung Unlock Ceremonies).

---

## 4. Nightly CI step

Per M2 plan MVP25: add a CI step that runs the core suite (from task_suite.yaml) on schedule. Use `schedules.yaml` → `nightly`; runner resolves suites to task list, executes, writes to `.llama_runtime/eval/results/` and reports to `.llama_runtime/eval/reports/`.
