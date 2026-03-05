# Experiment Budget (Creativity with Cost Control)

Creativity is encouraged, but must stay cheap and measurable.

## Core rule
Ideas must be phrased as **hypotheses** and validated with **small experiments**.

## Budget defaults
- Max experiments per run: **3**
- Max experiments per day: **6**
- Max time per experiment: **5 minutes** (or a single deterministic command)
- Max artifacts per experiment: keep evidence compact (logs + one report)

## When to use experiments
- New feature direction
- Unclear trade-off (cost vs reliability)
- Repeated planning disagreements

## Forbidden
- Open-ended research during execution
- Replanning the whole system without a trigger

## Required outputs
- HypothesisSpec (1–3 hypotheses)
- ExperimentSpec (1 experiment per hypothesis)
- Evidence folder under `validation_runs/YYYY-MM-DD/experiments/`
