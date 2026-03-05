# Task: Implement Skill `pdf_render` (NanoBanana PDF Quality)

## Ziel
Ein deterministischer Skill `pdf_render`, der ein druckfähiges PDF aus:
- Markdown-Manuskript (`Docs/Documentation/...`) und
- Diagramm-Assets (`.svg/.png`) erzeugt.

## Scope
- Markdown → PDF (A4), mit Überschriften, Codeblöcken, Listen
- Optional: TOC
- Diagramm-Einbettung über Platzhalter im Manuskript

## Contracts
- Inputs schema: `.claude/contracts/schemas/pdf_render_inputs.schema.json`
- Outputs schema: `.claude/contracts/schemas/pdf_render_outputs.schema.json`

## Platzhalter-Konvention im Manuskript
Im Markdown werden Diagramme so referenziert:

`<!-- DIAGRAM: <id> -->`

Der Renderer ersetzt den Platzhalter durch das gerenderte Asset (SVG bevorzugt, sonst PNG).

## Akzeptanzkriterien
- CLI via `python tools/skills/skill_runner.py --in request.json` unterstützt `pdf_render`.
- Ein Beispiel-Request aus `contracts/examples/pdf_render.skill_request.example.json` produziert:
  - PDF an `output_pdf_path`
  - Report in `outputs` mit `status=ok`
- Renderer ist deterministisch:
  - gleiche Inputs → identische PDF-Hash (innerhalb gleicher Tool-Version)

## Implementierungshinweise
- Python: `reportlab` für PDF-Layout.
- Markdown Parsing: `mistune` oder `markdown-it-py`.
- Code highlighting optional (Pygments).

## Evidence
- Lege Evidence unter `validation_runs/YYYY-MM-DD/...` an.
- Füge `determinism_harness` Run hinzu.
