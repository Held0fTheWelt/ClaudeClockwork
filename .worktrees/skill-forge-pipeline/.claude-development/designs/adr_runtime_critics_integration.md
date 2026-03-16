# ADR: Runtime Critics Integration

**Status:** Accepted (Design)  
**Date:** 2026-03-02  
**Context:** MVP22-D — Runtime Critics Architecture  
**Deciders:** Team Lead, M2 Design Sprint

---

## Context

Critics today are methodology-level (`.claude/agents/critics/*.md`). To support CI and post-run quality gates we need **runtime critics** that (a) produce machine-readable results, (b) integrate with the existing quality-signal pipeline, and (c) are gated by escalation level so they only run when appropriate.

## Decision

1. **Single result format:** Every runtime critic emits a **CriticResult** (see `critic_result.schema.json`). One result per critic per run; multiple results can be aggregated into a gate decision.
2. **Activation by escalation level:** A **critic_gates.yaml** defines which critics run at which escalation level (L0–L5). Example: drift_critic at L1+, regression_critic after any eval run.
3. **Integration point:** Results are (a) written to `.llama_runtime/outcome_ledger/critic_results.jsonl` (append, one JSON object per line), and (b) optionally fed into `llamacode/core/quality_signal.py` by mapping CriticResult → aggregated quality signal (e.g. severity_max, risk_flag) for downstream routing/telemetry.
4. **Pipeline order:** Gate flow: run skills/tests → run activated critics → collect CriticResults → compute gate pass/fail from critic severities and thresholds in critic_gates.yaml → persist results and optionally append to quality_signals.jsonl.

## Interface (Critic – Pipeline)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  Gate / CI      │────▶│  Critic Runner   │────▶│  drift_critic /          │
│  (gate.sh,      │     │  (invokes each   │     │  regression_critic /    │
│   eval_runner)  │     │   enabled critic)│     │  …                      │
└─────────────────┘     └────────┬─────────┘     └────────────┬────────────┘
                                 │                            │
                                 │  CriticResult (JSON)        │
                                 ▼                            │
┌─────────────────────────────────────────────────────────────▼─────────────┐
│  Collector                                                                 │
│  - Validates against critic_result.schema.json                             │
│  - Appends to .llama_runtime/outcome_ledger/critic_results.jsonl           │
│  - Evaluates critic_gates.yaml thresholds → gate pass/fail                │
│  - Optionally: map to QualitySignal and append to quality_signals.jsonl     │
└───────────────────────────────────────────────────────────────────────────┘
```

## Consequences

- **Positive:** Uniform contract for all runtime critics; gate and CI can treat every critic the same; escalation-level gating avoids unnecessary runs.
- **Negative:** Requires updating gate.sh and eval_runner (or a small orchestrator) to call the critic runner and consume critic_gates.yaml.
- **Follow-up:** MVP23 implements drift_critic and regression_critic; MVP28 adds the remaining 10 critics.
