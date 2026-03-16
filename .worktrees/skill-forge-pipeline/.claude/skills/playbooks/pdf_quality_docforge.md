# Playbook: NanoBanana PDF Quality (DocForge)

Ziel: Aus bestehenden Docs entstehen **publishing-grade** Dokumente + PDFs.

## Rollen & Modellkonfiguration
Diese Playbook nutzt 4 Ollama-Rollen:
- Explore
- Write
- Critic
- DecideGap

Konfiguration: `.claude/config/pdf_quality_ollama_profiles.yaml`

## Inputs (Source Pack)
Der Librarian stellt einen kompakten Source Pack bereit:
- Links/Pfade zu relevanten Dateien
- 10–30 Snippets (max 1500 Wörter total)
- Glossary (10–30 Terms)

Optional: `deliberation_pack_build` Skill, wenn Deep-Oodle nötig ist.

## Ablauf

### 1) Explore (Outline + Diagrammplan)
Output:
- Outline
- „Open Questions“ (max 8)
- Diagrammplan (welche Diagramme, Zweck, Datenquellen)

Stop, wenn Scope unklar ist → an Team Lead eskalieren.

### 2) Write (Manuskript v1)
- Verwende das passende Template.
- Schreibe in kurzen Absätzen, mit klaren Überschriften.
- Setze Diagramm-Platzhalter:
  - `<!-- DIAGRAM: system_overview -->`

Output:
- `Docs/Documentation/<doc_name>.md`
- Diagramm-Quellen (`.mmd` / `.dot`) in `Docs/References/diagrams/<doc_name>/`

### 3) Critic (Rubrik + Fixliste)
- Nutzt `skills/pdf_quality/rubric.md`.
- Liefert **Top 10 Fixes** (priorisiert) + Score.

Output:
- `Docs/Review/<doc_name>_critic.md`

### 4) DecideGap (Gap Report)
- Erstellt `QualityGapReport` (Schema).
- Entscheidet: 0/1/2 weitere Iterationen sinnvoll.

Output:
- `Docs/Review/<doc_name>_gap_report.json`

### 5) Render (deterministisch)
Wenn Manuskript stabil:
- Skill `pdf_render` ausführen

Output:
- PDF in `Docs/References/<doc_name>.pdf`

## Diagramm-Regeln
- Diagramme müssen auch in Schwarz/Weiß lesbar sein.
- Max 12 Knoten pro Diagramm (sonst split).
- Jedes Diagramm bekommt: Titel, Legende (wenn nötig), kurze Interpretation im Text.

## “Definition of Done”
- Score ≥ 85
- Keine offenen Widersprüche
- Mindestens 1 Diagramm pro Kernthema
- First Steps / Next Steps vorhanden


## Zusatz-Schritt: Grenzen sichtbar machen (Expectation Trap Pass)
Erzeuge für jedes Dokument zusätzlich eine kompakte Liste:

1) **Was kann es (noch) nicht**, obwohl man es intuitiv erwarten würde?
2) **Was ist ausdrücklich nicht Bestandteil** (Non-Goals) – inkl. "nicht geplant" vs "später vielleicht".
3) **Was ist denkbar**, aber derzeit nicht implementiert (Future Work / Möglichkeiten).

Das ist Pflicht-Input für den Writer und Pflicht-Check für den Critic.


## Vorstufe: Limitation Harvest (Pflicht vor dem Schreiben)
1) Run `limitation_harvest_scan` (deterministisch)
2) Der Writer MUSS die Ergebnisse in folgende Sektionen übernehmen:
   - **Limitierungen & Grenzen**
   - **Erwartungsfallen**
   - **Nicht-Ziele**
   - **Denkbar / Future Work**
3) Der Critic prüft explizit, ob die Harvest-Liste abgedeckt ist (oder bewusst verworfen wurde).
