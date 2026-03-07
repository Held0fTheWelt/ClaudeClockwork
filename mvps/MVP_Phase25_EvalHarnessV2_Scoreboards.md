# MVP Phase 25 — Eval Harness v2 (Scoreboards, Trends, Regression Tracking)

**Goal:** Move from “gates only” to measurable performance: scoreboards for quality/latency/failures, trend reports, and regression detection for routing + LocalAI capabilities.

**Why now:** With LocalAI and adaptive routing, you need evidence-driven optimization. CI should block regressions, and developers should see trends.

---

## Definition of Done

- [ ] Golden suites exist for at least 2 capabilities (e.g. embeddings + ASR)
- [ ] Scoreboard generator exists (JSON + Markdown summary)
- [ ] Trend tracking exists (p50/p95 latency, failure rates, quality proxies)
- [ ] CI gate blocks defined regressions (threshold-based)
- [ ] All existing tests pass

---

## H25.1 — Golden Suite Format

**Files:**
- `eval/golden_suites/` (new)
- `Docs/eval_golden_suite_format.md` (new)

**Change:**
- Define suite layout:
  - inputs (files or references)
  - expected outputs (exact or tolerance-based)
  - scoring function (quality proxy)
- Keep suite small and repo-friendly (or use hashed references).

**Acceptance:**
- Suites are deterministic and runnable locally + CI.

---

## H25.2 — Scoreboards + Trend Reports

**Files:**
- `claudeclockwork/eval/scoreboard.py`
- `Docs/eval_scoreboards.md`

**Change:**
- Generate:
  - `scoreboard.json` (machine-readable)
  - `scoreboard.md` (human summary)
- Store under runtime root (and optionally export redacted summaries to `.report/`).

**Acceptance:**
- Repeated runs produce consistent formatting and stable ordering.

---

## H25.3 — Regression Gates

**Files:**
- `claudeclockwork/core/gates/eval_regression_gate.py`
- `tests/test_eval_regression_gate.py`

**Change:**
- Gate compares current run vs baseline:
  - block if failure rate increases beyond threshold
  - block if latency p95 worsens beyond threshold
  - block if quality proxy drops beyond threshold

**Acceptance:**
- A synthetic regression triggers a deterministic failure.

---

## H25.4 — Router + LocalAI Integration

**Files:**
- Router modules (existing)
- LocalAI runtime modules (Phase 20)

**Change:**
- Ensure eval harness can:
  - test router decisions on a suite
  - test capability execution (mocked or real, depending on environment)

**Acceptance:**
- One command runs suites and produces scoreboard + gate result.

---
