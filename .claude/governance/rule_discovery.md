# Rule Discovery & Maintenance

## Grundprinzip

Die Regelbasis ist nie vollständig. Bei jedem Arbeitsschritt — insbesondere bei Task-Erstellung und Reviews — werden implizite, noch nicht dokumentierte Regeln aktiv identifiziert und in die Struktur einsortiert.

## Wann wird eine neue Regel erkannt?

Eine Regel gilt als erkennbar wenn mindestens eines zutrifft:

- **Wiederholung** — Ein Muster tritt in mehreren Modulen oder Funktionen konsistent auf
- **Konvention** — Code folgt einer einheitlichen Struktur, die nicht zufällig ist (Naming, Reihenfolge, Abhängigkeiten)
- **Constraint** — Eine Einschränkung der Sprache, des Frameworks oder der Architektur erzwingt ein bestimmtes Vorgehen
- **Fehlerquelle** — Ein Fehler tritt auf, dessen Ursache auf eine undokumentierte Regel zurückzuführen ist
- **Abweichung** — Code weicht von dokumentierten Regeln ab und die Abweichung erweist sich als korrekt → bestehende Regel anpassen
- **Architektur-Lücke** — Während der Arbeit wird sichtbar, dass die Architektur eine Regel impliziert, die noch nicht dokumentiert ist

## Ablauf bei Entdeckung

1. **Identifizieren** — Muster/Constraint/Konvention als noch nicht dokumentiert erkennen
2. **Einordnen** — Prüfen in welches `.claude/`-Dokument die Regel thematisch gehört:
   - Python-Patterns → `.claude/python/patterns.md`
   - Architekturregeln → `.claude/python/architecture.md`
   - Governance/Prozess → `.claude/governance/`
   - Projektübergreifende Erkenntnisse → `MEMORY.md`
3. **Einsortieren oder Anlegen** — In bestehendes Dokument einfügen ODER neues `.claude/`-Dokument anlegen
4. **`.claude/SYSTEM.md` aktualisieren** — Bei neuem Dokument: Quick Links + Unterordner-Referenz erweitern
5. **User informieren** — Kurz mitteilen welche Regel erkannt und wo eingetragen
6. **In Plan/Review dokumentieren** — Unter "Neu entdeckte Regeln" vermerken

## Qualitätskriterien für neue Regeln

- **Konkret** — Keine vagen Aussagen; nachprüfbare Regeln mit Beispielen oder Code-Snippets
- **Belegt** — Bezug auf konkreten Code, Fehler oder Architektur-Eigenschaft die die Regel begründet
- **Einsortiert** — Thematisch im richtigen Dokument, nicht als loses Anhängsel
- **Widerspruchsfrei** — Gegen bestehende Regeln gegenprüfen; bei Widerspruch ältere Regel aktualisieren oder User fragen

## Was NICHT aufgenommen wird

- Einmalige, projektspezifische Workarounds ohne Wiederholungspotenzial
- Ungeprüfte Vermutungen über Patterns, die nur auf einer einzelnen Datei basieren
- Informationen die bereits in `.claude/` oder `MEMORY.md` stehen

## Wann Rule Discovery obligatorisch ist

- Bei jedem Task: Workflow (Planerstellung)
- Bei jedem Review: Workflow
- Bei jedem Document: Workflow
- Bei jedem Implement: Workflow
