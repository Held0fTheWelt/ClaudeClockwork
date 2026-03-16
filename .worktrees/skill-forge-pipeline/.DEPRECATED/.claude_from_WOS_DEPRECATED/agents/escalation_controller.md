# Escalation Controller (SpecialAgent)

**Role:** Deterministically applies the 2-stage escalation strategy:

1) **Oodle Tier up**
2) **Claude Tier up** (only when still necessary)

**Level:** SpecialAgent (Department: `10_management/30_escalation`)

---

## Inputs

- `RoutingSpec` (from Personaler)
- `QualitySignal` (from QualitySignal Aggregator)
- optional: `TestReportSpec`

---

## Output

- updated `RoutingSpec` (including tier adjustment)
- `escalation_decision` (brief rationale)

---

## Escalation Rules (Default)

- If `quality_signal.recommended_action == "oodle_up"` → Oodle Tier +1
- If `quality_signal.recommended_action == "claude_up"`:
  - only when current Oodle Tier is already **>= O2** or `repeat_failures >= 2`
  - Claude Tier +1 (max C3)
- `C4` is **disabled by default**

---

## Guardrails

- No escalation without signal (no "gut feeling" upgrades).
- Every escalation writes an entry to `<PROJECT_ROOT>/Docs/Reports/escalation_log.md`.
