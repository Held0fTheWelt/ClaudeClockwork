# Rubric: PDF Quality (DocForge)

Diese Rubrik wird von **Critic** und **DecideGap** genutzt.

## Scoring (0–100)

### 1) Coverage (0–25)
- Deckt das Dokument den definierten Scope vollständig ab?
- Sind Annahmen und Non-Goals explizit?

### 2) Structure & Navigation (0–20)
- Klare Gliederung, sinnvolle Überschriften, Inhaltsverzeichnis (wenn >3 Seiten).
- Konsistente Terminologie.

### 3) Clarity & Readability (0–20)
- Kurze Absätze, klare Sätze, aktive Formulierungen.
- Zielgruppe getroffen (Einsteiger vs. Expert).

### 4) Correctness & Consistency (0–15)
- Keine internen Widersprüche.
- Pfade/Begriffe stimmen mit SSoT/Governance überein.

### 5) Visuals (0–15)
- Mindestens 1 sinnvolles Diagramm pro Kernthema.
- Diagramme sind lesbar (Schriftgröße, Kontrast, Legenden).

### 6) Actionability (0–5)
- Konkrete Next Steps, Beispiele, Checklisten, API-Usage.

## Quality Levels
- **90–100:** Release-tauglich (nur kosmetische Änderungen).
- **75–89:** Gut, aber 1–3 größere Lücken.
- **55–74:** Nutzbar, aber mehrere strukturelle/inhaltliche Lücken.
- **<55:** Neuaufbau/Scope-Klärung nötig.

## Critic Output (Pflichtformat)

- Score (0–100)
- Top 10 Fixes (priorisiert)
- 1 “Most Leverage Improvement” (der eine Schritt, der am meisten bringt)
- Diagramm-Feedback (wenn relevant)


## Erwartungsfallen, Nicht-Ziele, Zukunft (Pflicht)

Ein wirklich gutes Dokument macht **explizit**, was viele sofort erwarten würden – aber (noch) nicht vorhanden ist.

**Pflicht-Sektionen (je nach Dokumenttyp):**
- **Limitierungen & Grenzen (Stand heute)**
- **Was es ausdrücklich NICHT ist (Non-Goals / Nicht-Ziele)**
- **Was viele erwarten würden, aber (noch) nicht implementiert ist (Expectation Traps)**
- **Was denkbar ist (Future Work / Möglichkeiten), aber derzeit nicht Teil des Systems**

**Scoring (0–5):**
- 0: fehlt komplett
- 3: vorhanden, aber generisch / ohne konkrete Beispiele
- 5: konkret, testbar, mit klaren Aussagen + Auswirkungen (z. B. Sicherheit/Performance/Scope)



## Limitation Harvest Coverage (0–5)

Bewertet, ob das Dokument die deterministisch geharvesteten Punkte (Expected-but-missing, Nicht-Ziele, Future Work) abdeckt.

- 0: Harvest ignoriert
- 3: teilweise übernommen, ohne Auswirkungen/Beispiele
- 5: vollständig und konkret, inkl. Auswirkungen + klare Abgrenzungen
