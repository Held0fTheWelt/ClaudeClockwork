# Decision Policy

## Entscheidungs-Hierarchie

Jede Entscheidung fällt in eine von drei Kategorien: autonom, Review-pflichtig, oder User-Bestätigung erforderlich.

---

## Autonome Entscheidungen (L0)

Kein Review erforderlich. Specialist Agent entscheidet selbst.

**Beispiele:**
- Kleinere Refactors innerhalb einer Datei
- Code-Formatierung, Kommentare
- Dokumentations-Updates ohne inhaltliche Änderungen
- Logging-Verbesserungen (keine API-Änderung)
- Bugfixes mit klarer, isolierter Ursache

**Kennzeichen:** Änderung betrifft max. 1 Datei, keine öffentliche API, keine Laufzeit-Auswirkungen außerhalb der Datei.

---

## Team Lead Review (L1)

Team Lead prüft und kann autonom freigeben. Kein Architecture Agent oder User notwendig.

**Beispiele:**
- Multi-Datei-Refactors (2–5 Dateien, klar abgegrenzt)
- Neue private Methoden / interne Hilfsfunktionen
- Moderate Refactors ohne API-Änderung

**Kennzeichen:** Mehrere Dateien betroffen, aber keine öffentlichen Schnittstellen geändert.

---

## Architecture Agent Mandatory Review (L2)

Architecture Agent muss vor Implementation freigeben.

**Beispiele:**
- Neue Top-Level-Module in `src/` (neues Modul vs. Erweiterung?)
- Neues Python-Package als Abhängigkeit (alles außerhalb stdlib)
- Modul-Boundary-Änderungen in `src/`
- Dependency-Richtungsänderungen (z.B. `config` soll `agents` importieren)
- Öffentliche API-Änderungen an `orchestrator.py` oder `ollama_client.py`

**Eskalations-Format:**
```
Problem:        [Was soll geändert werden und warum?]
Optionen:       [Mindestens 2 Alternativen]
Trade-offs:     [Pro/Contra für jede Option]
Empfehlung:     [Welche Option wird empfohlen + Begründung]
```

---

## Technical Critic Mandatory Review (L3)

Technical Critic gibt adversarielle Bewertung. Team Lead entscheidet danach.

**Beispiele:**
- Performance-kritische Pfade (Ollama-Client-Timeout-Handling)
- subprocess-Pooling oder parallelisierte Agent-Spawns
- Externe API-Integration (Claude-CLI-Interface-Änderungen)
- Persistente Datenstruktur-Änderungen (Docs/-Schema, Config-Format-Änderungen)

---

## Systemic Critic Mandatory Review (L4)

Systemic Critic bewertet Langzeit-Komplexität. Team Lead entscheidet danach.

**Beispiele:**
- Neue Agent-Typen hinzufügen
- Governance-Regeln ändern
- Self-Improvement-Zyklus verändern
- Eskalationsschwellen anpassen
- `.claude/` Systemstruktur reorganisieren

---

## User-Bestätigung Erforderlich (L5)

Keine autonome Entscheidung möglich. User entscheidet.

**Beispiele:**
- Orchestrator-Core-Redesign
- Wechsel des LLM-Backends
- Grundlegende Änderung des Workflow-Trigger-Systems

---

## Konflikt-Resolution

Wenn Architecture Agent und Technical/Systemic Critic widersprechen:

```
1. Team Lead fasst Trade-offs zusammen
2. Risk-Level kategorisieren (Low / Medium / High)
3. Bei L3+: User trifft finale Entscheidung
4. Entscheidung wird im Performance-Log dokumentiert
```

---

## Eskalations-Vorlage

```markdown
## Eskalation: [Titel]
**Level:** L2 / L3 / L4 / L5
**Datum:** YYYY-MM-DD
**Initiiert von:** [Agent]

### Problem
[Was ist die Situation? Warum ist Entscheidung nötig?]

### Optionen
**Option A:** [Beschreibung]
**Option B:** [Beschreibung]

### Trade-offs
| Kriterium | Option A | Option B |
|---|---|---|
| Komplexität | | |
| Performance | | |
| Wartbarkeit | | |

### Empfehlung
[Klare Empfehlung mit Begründung]
```
