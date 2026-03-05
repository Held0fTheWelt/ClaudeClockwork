# Execution Protocol — Python Orchestrator

> Verbindliches Ablaufprotokoll für Claude Code und alle Agent-Spawns.
> Gilt für alle Tasks unabhängig vom Trigger.

---

## Schritt 1 — Canonical Sources lesen

Immer zuerst:
1. `CLAUDE.md` + `.claude/SYSTEM.md` — Projekt-Identität, Modul-Hierarchie, Patterns
2. `<PROJECT_ROOT>/MEMORY.md` — Stabiles Cross-Session-Wissen (Team Lead liest das zuerst)
3. `governance/workflow_triggers.md` — Trigger-Routing, Dokument-Naming

---

## Schritt 2 — Task klassifizieren

Escalation Level bestimmen (→ `governance/decision_policy.md`):

| Level | Wer entscheidet | Typische Situation |
|---|---|---|
| L0 | Specialist autonom | 1 Datei, keine API-Änderung |
| L1 | Team Lead | 2–5 Dateien, klar abgegrenzt |
| L2 | Architecture Agent | Neues Modul, neue Abhängigkeit |
| L3 | Technical Critic | Performance-Pfade, externe API |
| L4 | Systemic Critic | Governance-Änderungen, neue Agent-Typen |
| **L5** | **User — STOPP und fragen** | Orchestrator-Redesign, Backend-Wechsel |

**Kleinste ausreichende Modell-Größe wählen** (→ Ollama hardware routing in `ollama_integration.md`).

---

## Schritt 3 — L5-Gates prüfen (vor jeder Aktion)

**User-Bestätigung zwingend erforderlich bei:**
- Externen Providern oder API-Keys
- Angeforderter Tool-Autonomie (automatisierte Bash-Ausführung)
- Destruktiven Operationen oder großen Refactors
- Anhaltendem Widerspruch nach Critic-Review
- Core-Orchestrator-Redesign oder LLM-Backend-Wechsel

---

## Schritt 4 — Arbeit in kleinen, prüfbaren Schritten

**Ausführungs-Phasen** (in dieser Reihenfolge):

```
intake → plan → build → validate → review → docs → archive
```

- **intake (Low-Effort-Diener)**: Trigger erkennen, Subject erfassen, Kontext laden (Librarian) und strukturieren. Nur Vorbereitung: Quellen sammeln, betroffene Dateien/Diffs identifizieren, kurze Intake-Notiz. **Keine** Bewertung, keine Architekturentscheidungen.
- **plan**: Plan-Dokument erstellen (`Docs/Plans/Plan_<Name>.md`), User-Freigabe
- **build**: Implementierung durch Specialist Agent (mit Ollama-Briefing bei L1+; typischerweise Medium/High Effort nach Low-Effort-Intake)
- **validate**: Validation Agent prüft Syntax, Imports, Patterns
- **review**: Review-Dokument erstellen, bei L3+ Critic aktivieren
- **docs**: Documentation Agent aktualisiert Docs/ und MEMORY.md
- **archive**: Entscheidung in `.claude/knowledge/decisions.md` eintragen; bei abgeschlossenem Plan **Task-Archivierung (BP-005)** ausführen → siehe `governance/task_archival.md`

**Minimal-Kontext-Prinzip:** Jeder Agent bekommt nur was er braucht. Librarian baut Context-Packs.

---

## Schritt 5 — Ollama-Gate (bei L1+)

```python
from src.ollama_client import OllamaClient, OllamaUnavailableError

client = OllamaClient()
if level >= 1 and not client.is_available():
    raise OllamaUnavailableError("Ollama not reachable — FREEZE")
```

→ Wenn unavailable: **FREEZE** — kein Teilimplementieren ohne Briefing.
→ Vollständiges Protokoll: `governance/ollama_integration.md § Freeze Protocol`

---

## Schritt 6 — Nach jedem Schritt

- **Smoke check** ausführen: `python3 src/main.py --task "test ollama"` (bei Code-Änderungen)
- **Docs aktualisieren** wenn Verhalten geändert (CLAUDE.md, Agent-Definitionen)
- **Signifikante Entscheidungen** eintragen in `.claude/knowledge/decisions.md`

---

## Schritt 7 — Shell / Patch-Anwendung

- **Manual-only per Default.** Keine Shell-Befehle oder Patches ohne explizite User-Freigabe.
- Ausnahme: Bash-Tool-Permissions in `settings.local.json` (nur die dort gelisteten Befehle).

---

## Schritt 8 — Dokument-Abschluss

Jede Task endet mit:
1. Plan-Status auf `IMPLEMENTED` oder `CLOSED` setzen
2. Abweichungen vom Plan dokumentieren (inline im Plan-Dokument)
3. MEMORY.md updaten (wenn stabile neue Erkenntnis)
4. Decisions.md updaten (wenn Architekturen- oder Policy-Entscheidung)
5. **Archivierung (BP-005):** Task in der Task-Liste als erledigt markieren; bei abgeschlossenem Plan Agentensystem für Archivierung anstoßen (Ergebnisse → `Docs/References/`, `Docs/Documentation/`, `.claude/knowledge/index.md`) — vollständiges Protokoll: `governance/task_archival.md`
