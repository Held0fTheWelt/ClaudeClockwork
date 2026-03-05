# Dokument-Platzierungskorrektur (BP-006)

> Dokumente, die vom Owner oder durch frühere Tasks falsch abgelegt wurden, werden von einem Team an den richtigen Ort verschoben — mit Rücksprache beim Owner.

---

## Zweck

- **Konsistenz:** Alle Dokumente liegen an den in Governance und File Ownership definierten Orten.
- **Auffindbarkeit:** Falsche Ablage führt zu falschem Routing und verlorener Information.
- **Owner-Rücksprache:** Ob im konkreten Fall immer so verfahren werden soll, wird mit dem Owner geklärt.

---

## Wann greift BP-006?

- Ein Agent oder ein Review stellt fest: Ein Dokument liegt **nicht** am laut `file_ownership.md` und `workflow_triggers.md` (Dokument-Naming, Ablageorte) vorgesehenen Platz.
- Beispiele: Referenz-Inhalt in `Docs/Plans/`, Plan in `Docs/Documentation/`, technische Doc in `Docs/References/` obwohl es Feature-Dokumentation ist.

---

## Ablauf (Platzierungskorrektur)

1. **Feststellung**
   - Der feststellende Agent/Review dokumentiert: welche Datei, aktueller Ort, begründeter Zielort (inkl. Verweis auf `file_ownership.md` / Dokument-Naming).

2. **Meldung an Team Lead**
   - Team Lead wird informiert: "Dokument [Pfad] ist vermutlich falsch abgelegt; vorgeschlagener Zielort: [Ziel]."

3. **Rücksprache mit Owner**
   - **Owner** ist der laut `file_ownership.md` für den **Zielort** (oder Quellort) zuständige Agent bzw. der User (Product Owner), wenn das Dokument vom User stammt.
   - Team Lead koordiniert Rücksprache:
     - Soll das Dokument an den vorgeschlagenen Ort verschoben werden?
     - Soll für vergleichbare Fälle künftig immer so verfahren werden? (Falls ja → ggf. Regel in Governance oder MEMORY.md festhalten.)

4. **Verschiebung**
   - Nach Freigabe führt der **Owner** des Zielorts die Verschiebung durch (Inhalt an neuen Ort, ggf. alte Datei entfernen oder als Verweis ersetzen).
   - Cross-References und `.claude/knowledge/index.md` werden vom Librarian Agent angepasst.

5. **Keine stille Verschiebung**
   - Kein Agent verschiebt Dokumente ohne Meldung und ohne abgesprochene Freigabe. Sonst drohen Doppelungen, verlorene Verweise und Verletzung der File Ownership.

---

## Ownership bei Verschiebung

- **Verschieben** darf nur, wer entweder Owner der Quell-Datei oder Owner des Zielorts ist (siehe `file_ownership.md`).
- Wenn der feststellende Agent nicht Owner ist: Domain Handoff an Team Lead → Team Lead aktiviert den zuständigen Owner für die Verschiebung.

---

## Dokumentation

- Signifikante Korrekturen (z. B. neues Standardvorgehen "immer so") in `<PROJECT_ROOT>/MEMORY.md` oder `.claude/knowledge/decisions.md` festhalten.
- Kein separates Dokument pro Verschiebung nötig; bei Bedarf im Review oder in der Task-Liste vermerken.
