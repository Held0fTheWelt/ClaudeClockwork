# Task-Archivierung (BP-005)

> Implementierte Tasks verschwinden aus der aktiven Liste; Ergebnisse landen in Referenzen, Feature-Docs und Knowledge-Index.
> Gilt für Claude Code und alle Agent-Spawns nach Abschluss eines Plans.

---

## Zweck

- **Übersicht:** Aktive Task-Liste bleibt klein und aktuell.
- **Auffindbarkeit:** Ergebnisse werden in Referenz- und Feature-Dokumenten sowie im Knowledge-Index verankert.
- **Netzwerk:** Alle Agents können zukünftig auf die relevanten Informationen zugreifen.

---

## Wann greift BP-005?

- Plan-Status wurde auf `IMPLEMENTED` oder `CLOSED` gesetzt.
- Die zugehörige Task-Beschreibung (falls in `Docs/Tasks/` oder `Docs/Plans/` als Task_* geführt) gilt als abgeschlossen.

---

## Ablauf (Archivierungs-Phase)

1. **Erledigt markieren**
   - In der aktuellen Task-Übersicht (z. B. `<PROJECT_ROOT>/Docs/TASKS.md`, Task-Index in `.claude/knowledge/index.md` oder zentrale Task-Liste) den Task als erledigt kennzeichnen.
   - Plan-Dokument: Status auf `IMPLEMENTED` oder `CLOSED` setzen (siehe Execution Protocol Schritt 8).

2. **Archivierungs-Workflow anstoßen**
   - Team Lead koordiniert die Archivierung.
   - Beteiligte Agents (ohne direkte Agent-zu-Agent-Imports):
     - **Librarian Agent:** Ergebnisse in passende Referenzdokumente überführen (`Docs/References/`, Namensschema `Ref_<Thema>.md`), Cross-References pflegen, `.claude/knowledge/index.md` aktualisieren.
     - **Documentation Agent:** Feature- bzw. Funktionsbeschreibungen in `Docs/Documentation/` anlegen/aktualisieren, mit klaren Verknüpfungen zu Code und Referenzen.

3. **Ablageorte**
   - **Referenzwissen:** `Docs/References/Ref_<Thema>.md` — Architektur- und System-Referenzen.
   - **Feature-/Technik-Docs:** `Docs/Documentation/` — Beschreibung der umgesetzten Features und technischen Details.
   - **Knowledge-Index:** `.claude/knowledge/index.md` — neue oder geänderte Dateien eintragen, Themen-Tags und Vollständige Datei-Karte pflegen.

4. **Neue Dokumenttypen**
   - Sollen zusätzliche Dokumentklassen (z. B. neuer Ordner, neues Präfix) eingeführt werden, ist dies mit dem **Product Owner** (User) zu vereinbaren. Erst nach Freigabe anlegen und in Governance (z. B. `workflow_triggers.md`, `file_ownership.md`) dokumentieren.

---

## Integration in den Execution Flow

- Die Phase **archive** in `execution_protocol.md` umfasst:
  - Eintrag in `.claude/knowledge/decisions.md` (bereits definiert),
  - **plus** die hier beschriebene Archivierung (Ergebnisse → Ref + Documentation + Index).
- Optional kann ein expliziter Trigger **Archive:** in `workflow_triggers.md` genutzt werden, um eine reine Archivierungs-Task auszulösen (z. B. nachträglich für ältere abgeschlossene Tasks).

---

## Verantwortlichkeiten (File Ownership)

| Aktion | Owner |
|--------|--------|
| Task-Liste / Plan-Status aktualisieren | Team Lead |
| `Docs/References/` anlegen/ändern | Librarian Agent |
| `Docs/Documentation/` anlegen/ändern | Documentation Agent |
| `.claude/knowledge/index.md` aktualisieren | Librarian Agent |
| `.claude/knowledge/decisions.md` Eintrag | Team Lead |

Domain Handoff über Team Lead, wenn ein Agent Schreibrechte in einer anderen Domain benötigt (siehe `file_ownership.md`).
