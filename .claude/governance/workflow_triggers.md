# Workflow Triggers & Document Naming


# Workflow Triggers

Kleinste ausreichende Modell-Größe und minimaler Aufwand.

**L5-Eskalation an User** bei:
- Externen Providern / API-Keys
- Angeforderter Tool-Autonomie (automatisierte Bash-Ausführung)
- Destruktiven Operationen oder großen Refactors
- Anhaltendem Widerspruch nach Critic-Review
- Core-Orchestrator-Redesign oder LLM-Backend-Wechsel

Für komplexe Coding-Tasks → `qwen2.5-coder:32b` (CPU); für Architektur → `phi4:14b` (GPU).


## Trigger-Stichwörter

Der User löst Workflows durch diese Stichwörter aus:

| Stichwort | Workflow | Erzeugt Dokument in |
|---|---|---|
| **Task:** | Planerstellung | `Docs/Plans/Plan_<Name>.md` |
| **Review:** | Review erstellen | `Docs/Review/Review_<Name>.md` |
| **Critics:** | Grundsätzliche Kritik | `Docs/Critics/Critics_<Schweregrad>_<Name>.md` |
| **Document:** | Dokumentation erzeugen/verbessern | `Docs/Documentation/` oder `Docs/References/` |
| **Implement:** | Plan implementieren | Code-Änderungen |
| **Archive:** | Task-Archivierung (BP-005) auslösen | Ref + Documentation + Index (nach Plan-Abschluss) |
| **test ollama** | Ollama Funktionstest | (kein Dokument) |

## Task: Workflow (Planerstellung)

**Planungspflichtig wenn:** Architektur-Auswirkungen vorhanden:
- Neue oder geänderte Komponenten, Plugins, Interfaces
- Änderungen an Datenfluss, Abhängigkeiten oder Systemverhalten
- Auswirkungen auf mehr als eine isolierte Stelle

**Kein Plan nötig bei:** Einzeiligen Fixes, Tippfehlern, reinen Konfigurationsänderungen ohne Architektureinfluss.

**Ablauf:**
1. Anforderung erfassen als `Task_<Name>.md` in `Docs/Plans/`
2. Regelprüfung via .claude/SYSTEM.md — alle relevanten Dokumente konsultieren
3. Rule Discovery — aktiv nach undokumentierten Regeln suchen
4. Plan-Dokument erstellen
5. User-Freigabe einholen

**Plan-Dokument Format:**
```
# Plan: <Titel>
## Ziel
## Geprüfte Regeln
## Betroffene Dateien
## Implementierungsschritte
## Neu entdeckte Regeln
## Offene Fragen
```

Plan-Iteration: Dokument aktualisieren bis zur Implementierung (kein neues Dokument pro Iteration).

## Review: Workflow

**Review-Gegenstände:**
- Plan (vor Implementierung) — ist der Plan regelkonform, vollständig, umsetzbar?
- Implementierung (nach Task-Ausführung) — entspricht die Umsetzung dem Plan und den Regeln?
- Komponente/Systemzustand — aktueller Zustand eines Teilsystems

**Ablauf:**
1. Gegenstand bestimmen (Plan / Implementierung / Komponente)
2. Referenz-Plan laden aus `Docs/Plans/` (falls vorhanden)
3. Regelprüfung via .claude/SYSTEM.md
4. Rule Discovery
5. Review-Dokument in `Docs/Review/` ablegen

**Review-Dokument Format:**
```
# Review: <Titel>
## Review-Gegenstand
## Prüfergebnis
### Regelkonformität
### Plan-Abweichungen
### Kritik
## Bewertung
- [ ] Regelkonform
- [ ] Plankonform (falls zutreffend)
- [ ] Keine offenen Mängel
## Neu entdeckte Regeln
## Empfehlung
```

**Rework-Zyklus:** Konkrete Punkte → Plan überarbeiten → neues Review → bis zur Freigabe.

## Critics: Workflow

**Abgrenzung von Review:**
- Review: "Entspricht das den Regeln?" → `Docs/Review/`
- Critics: "Ist der Ansatz fundamental falsch?" → `Docs/Critics/`

**Schweregrade:**
- `Critics_Minor_` — Plan-Ebene: Designentscheidung hinterfragbar, kein strukturelles Problem
- `Critics_Normal_` — Review-Ebene: konkretes Problem in Implementierung/Review erkannt
- `Critics_Major_` — Systemebene: fundamental falsch angelegt, Neuausrichtung nötig

**Critic-Dokument Format:**
```
# Critic: <Fragestellung>
## Untersuchungsgegenstand
## Ist-Zustand
## Grundsätzliche Kritik
## Auswirkungen
## Lösungsrichtung
## Neu entdeckte Regeln
```

Critic-Dokumente sind Langzeit-Referenzen. Ein Critic kann neuen Task oder Regeländerung auslösen — aber nur auf User-Entscheidung.

## Document: Workflow

Dokumentation aus drei Quellen:
1. .claude/ System (SSoT)
2. Bestehende Docs/
3. Source Code

Ablageorte:
- Funktionalitäts-Dokumentation → `Docs/Documentation/`
- Technische Definitionen → `Docs/Documentation/`
- Referenzdokumente → `Docs/References/`

## Implement: Workflow

**Voraussetzungen:**
- Plan-Dokument existiert in `Docs/Plans/Plan_<Name>.md`
- Plan durch Review freigegeben ODER User bestätigt explizit

**Ablauf:**
1. Plan laden
2. Bestätigung einholen — Plan kurz zusammenfassen + explizit fragen ob implementieren
3. Regelprüfung
4. Rule Discovery während Implementation
5. Implementierung ausführen
6. Plan-Status aktualisieren

Abweichungen vom Plan während der Implementierung sofort dokumentieren und User mitteilen.

**Nach Abschluss:** Archivierung (BP-005) — Task als erledigt markieren, Ergebnisse in `Docs/References/`, `Docs/Documentation/` und `.claude/knowledge/index.md` hinterlegen. Siehe `governance/task_archival.md`.

## Archive: Workflow (BP-005)

**Trigger:** Explizites Stichwort **Archive:** oder automatisch nach Implement-Abschluss (Plan `IMPLEMENTED`/`CLOSED`).

**Zweck:** Abgeschlossene Task-Ergebnisse in Referenz- und Feature-Dokumente überführen, Knowledge-Index aktualisieren, Task aus aktiver Liste nehmen.

**Ablauf:**
1. Abgeschlossene Task/Plan identifizieren
2. Team Lead koordiniert Librarian + Documentation Agent (über Domain Handoff)
3. Librarian: Ref-Dokumente in `Docs/References/`, Index `.claude/knowledge/index.md` aktualisieren
4. Documentation Agent: Feature-/Technik-Docs in `Docs/Documentation/` anlegen/aktualisieren
5. Task in Task-Übersicht als erledigt markieren

Vollständiges Protokoll: `governance/task_archival.md`.

## test ollama — Workflow

Führt einen Hello-World-Funktionstest für das lokale Ollama-System durch.

**Auslöser:** User gibt `test ollama` ein — typischerweise am Anfang einer Arbeitssession oder nach Ollama-Neustart.

**Ablauf:**
1. Ausführen: `python3 src/main.py --task "test ollama"`
   (alternativ direkt: `python3 .claude/tools/test_ollama.py`)
2. Script prüft: Erreichbarkeit → Modellverfügbarkeit → Inferenz → Python Output-Qualität
3. Bei PASS: Agent bestätigt "Ollama operational — bereit für Tasks"
4. Bei FAIL: Agent gibt FREEZE-Report aus (s. ollama_integration.md § Freeze Protocol)

**Kein Dokument wird erzeugt.** Der Test ist ein reiner Statuscheck.

---

## Dokument-Naming-Konvention

```
<Präfix>_<ThemaOderFeatureName>.md
```

| Dokumenttyp | Präfix | Ablageort |
|---|---|---|
| Task-Beschreibung | `Task_` | `Docs/Plans/` |
| Plan | `Plan_` | `Docs/Plans/` |
| Review | `Review_` | `Docs/Review/` |
| Kritik (Minor) | `Critics_Minor_` | `Docs/Critics/` |
| Kritik (Normal) | `Critics_Normal_` | `Docs/Critics/` |
| Kritik (Major) | `Critics_Major_` | `Docs/Critics/` |
| Referenz | `Ref_` | `Docs/References/` |

**Dokumentkette:** Zusammengehörige Docs teilen denselben Thema-Teil:
```
Task_OllamaClient.md
Plan_OllamaClient.md
Review_OllamaClient.md
Critics_Normal_OllamaClient.md
```

Thema-Teil in PascalCase. Mehrere Reviews/Critics zum selben Thema: Suffix ergänzen (z.B. `_PostImpl`).
Bestehende Dokumente ohne Konvention: bei nächster Bearbeitung umbenennen.
