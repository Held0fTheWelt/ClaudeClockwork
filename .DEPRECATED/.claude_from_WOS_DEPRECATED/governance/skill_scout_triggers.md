# Skill Scout Triggers (Hard Policy)

The Skill Scout must remain a **silent, low-cost observer**. It only runs when triggers fire.
This prevents unnecessary agent activity and token spend.

---

## Allowed Triggers (any one is sufficient)

### T1 — Repeat Failures
Run Skill Scout if:
- `repeat_failures >= 2` (same failure class OR same MVP/task type)

### T2 — Waste Signal (from Ops Ledger)
Run Skill Scout if any of the following is true:
- `redundant_rereads >= 2`
- `pack_bloat_events >= 1`
- `over_escalations >= 1`
- `drift_events >= 1`

### T3 — Explicit Request
Run Skill Scout only if:
- Team_Lead OR Personaler sets `explicit_skill_scout=true`

### T4 — Low-frequency cadence
Run Skill Scout at most:
- **once per day** OR once per campaign
and only if there were runs within the last 24 hours.

---

## Forbidden Conditions (must NOT run)

- Single, non-repeating failures without a pattern
- Missing evidence bundles (request evidence first)
- While an incident fix-loop is actively running (do not interrupt)

---

## Cost Policy

### Default
- Claude tier: **C1 (Haiku)** for concise reporting/relay
- No local O3 unless the O3 triggers below apply

### O3 Triggers (Local 70/72B is allowed only then)
Local O3 may be used only if:
- `repeat_failures >= 3`, OR
- `over_escalations >= 2`, OR
- `drift_events >= 2`, OR
- there are **>= 3 comparable runs** worth of compact evidence for clustering.

Local O3 must only receive compact evidence:
- OpsLedgerSummary
- QualitySignal
- short extracts (not full chats, not full repos)

---

## Output Limits

- Max **3** skill candidates per report.
- Each candidate must include:
  - trigger pattern
  - expected savings (low/med/high)
  - risk (low/med/high)
  - minimal scope (1 tool script + optional 1 schema + examples)
  - required inputs/outputs
- If uncertain: `recommendation = observe_more`
