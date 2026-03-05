# Performance Log Template

Kopiere dieses Template für jeden abgeschlossenen Major Task.
Speicherort: `Docs/Reviews/PerfLog_YYYY-MM-DD_[TaskName].md`

---

## Task Metadata

- **Task ID:** [Kurzname oder Nummer]
- **Datum:** YYYY-MM-DD
- **Initiiert von:** User / Team Lead / System
- **Team Lead:** [Name/Rolle]
- **Agents Involved:** [Liste aller beteiligten Agents]
- **Eskalationslevel:** L0 / L1 / L2 / L3 / L4 / L5

---

## Task Description

(Kurze Zusammenfassung: Was war das Ziel? Was wurde implementiert?)

---

## Estimated vs. Actual Complexity

- **Initial Estimate:** Minor / Moderate / Major / Critical
- **Final Measured:** Minor / Moderate / Major / Critical
- **Abweichung:** [Begründung wenn abweichend]

---

## Execution Metrics

- **Implementation Time:** [grob, z.B. "1 Session", "30 min"]
- **Review Time:** [grob]
- **Rework Count:** [Anzahl Rework-Zyklen]
- **Errors Detected:** [Anzahl Build-Fehler, Logic-Fehler]
- **Validation Failures:** [Anzahl]

---

## Python-Specific Metrics (wenn anwendbar)

- **Import Errors:** [Anzahl und Art]
- **Ollama-Calls:** [Anzahl und task_type]
- **Subprocess-Calls:** [Anzahl claude-CLI Spawns]
- **Docs-Dateien erzeugt:** [Anzahl und Pfade]

---

## Critic Reviews

### Technical Critic Findings
- **Weakness:** [Hauptbefund oder "None"]
- **Risk Level:** Low / Medium / High / Critical / N/A
- **Suggested Alternative:** [wenn vorhanden]

### Systemic Critic Findings
- **Structural Concern:** [Hauptbefund oder "None"]
- **Long-Term Risk:** [wenn vorhanden]
- **Simplification Proposal:** [wenn vorhanden]

---

## Lessons Learned

- **Was hat gut funktioniert?** [konkret]
- **Was hat Reibung verursacht?** [konkret]
- **Was sollte sich beim nächsten Mal ändern?** [konkret]

---

## Knowledge Updates

- **Documentation Updated:** [Welche Docs?]
- **Patterns Extracted:** [Welche neuen Patterns in patterns.md?]
- **Archived References Added:** [Welche neuen Referenzen in Docs/References/?]
- **MEMORY.md Updated:** Ja / Nein

---

## Improvement Proposal

(Spezifischer Governance- oder Prozess-Verbesserungsvorschlag — oder "None")
