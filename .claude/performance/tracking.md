# Performance Tracking

## Zweck

Fortlaufende Messung der System-Effektivität — auf Agent-Ebene und auf System-Ebene.

---

## Per-Agent Metriken

| Metrik | Beschreibung | Gut | Schlecht |
|---|---|---|---|
| Task Completion Success | Abschluss ohne Rework im 1. Versuch | >80% | <60% |
| Error Rate | Fehler pro Task (Build-Fehler, Logic-Fehler) | <2 | >5 |
| Rework Frequency | Wie oft muss derselbe Task zurückgegeben werden | 0–1 | >2 |
| Estimation Accuracy | Geschätzte vs. tatsächliche Komplexität | ±1 Level | >±2 Level |

---

## System-Level Metriken

| Metrik | Beschreibung |
|---|---|
| Knowledge Growth | Neue Patterns / Referenzen pro 10 Tasks |
| Documentation Coverage | % der implementierten Systeme mit aktuellen Docs |
| Refactor Frequency | Wie oft werden bereits abgeschlossene Tasks erneut angefasst |
| Architecture Stability | Anzahl L5-Eskalationen pro Monat (weniger = besser) |

---

## Log-Format

Performance-Logs werden nach `performance/log_template.md` im Projektverzeichnis gespeichert.
Datei-Namensschema: `Docs/Reviews/PerfLog_YYYY-MM-DD_[TaskName].md`

---

## Aggregation

Nach je **10 abgeschlossenen Major Tasks** erstellt Team Lead einen Aggregations-Report:

```markdown
## Performance Report: Tasks [N-M]
**Zeitraum:** YYYY-MM-DD bis YYYY-MM-DD

### Erfolgsraten
- Completion ohne Rework: X%
- Durchschnittliche Rework-Zyklen: Y

### Eskalations-Analyse
- L0: N Tasks
- L1: N Tasks
- L2: N Tasks  [Designer involviert]
- L3+: N Tasks [Critics involviert]

### Häufigste Probleme
1. [Problem-Typ] — [N] mal aufgetreten
2. [Problem-Typ] — [N] mal aufgetreten

### Verbesserungs-Empfehlung
[Konkrete Maßnahme mit Begründung]
```

---

## Eskalation bei Performance-Degradation

Wenn innerhalb von 10 Tasks:
- Rework-Frequency > 3 im Schnitt → Team Lead überprüft Task-Brief-Qualität
- Estimation Accuracy > ±2 Level → Komplexitäts-Klassifikation überarbeiten
- L3+ Eskalationen > 30% aller Tasks → Systemic Critic Überprüfung anfordern
