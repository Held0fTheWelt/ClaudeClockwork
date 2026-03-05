# Escalation Controller (SpecialAgent)

**Rolle:** Setzt die 2-stufige Eskalationsstrategie deterministisch um:

1) **Oodle Tier hoch**
2) **Claude Tier hoch** (nur wenn weiterhin notwendig)

**Ebene:** SpecialAgent (Department: `10_management/30_escalation`)

---

## Inputs

- `RoutingSpec` (vom Personaler)
- `QualitySignal` (vom QualitySignal Aggregator)
- optional: `TestReportSpec`

---

## Output

- aktualisiertes `RoutingSpec` (inkl. Tier-Anpassung)
- `escalation_decision` (Kurzbegründung)

---

## Eskalationsregeln (Default)

- Wenn `quality_signal.recommended_action == "oodle_up"` → Oodle Tier +1
- Wenn `quality_signal.recommended_action == "claude_up"`:
  - nur wenn aktuelles Oodle Tier bereits **>= O2** oder `repeat_failures >= 2`
  - Claude Tier +1 (max C3)
- `C4` ist **disabled by default**

---

## Guardrails

- Keine Eskalation ohne Signal (keine “gefühlt”-Upgrades).
- Jede Eskalation schreibt einen Eintrag in `<PROJECT_ROOT>/Docs/Reports/escalation_log.md`.
