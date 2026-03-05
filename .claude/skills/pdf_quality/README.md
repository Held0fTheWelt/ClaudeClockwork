# Skill: NanoBanana PDF Quality (DocForge)

Ziel: Aus vorhandenen Projekt-Dokumenten (Specs/Runbooks/Tasks/Notes) entstehen **lesbare, druckfähige PDFs** mit **passenden Grafiken und Schemata**.

Dieses Skill-Pack ist für **Claude Clockwork** gedacht:
- **LLM-Teil (nicht deterministisch):** Explore/Write/Critic/DecideGap erzeugen `manuscript.md` + Diagramm-Quellen.
- **Tool-Teil (deterministisch):** `pdf_render` rendert ein PDF aus Manuskript + Diagramm-Assets.

> Wichtig: In Clockwork sind Skills tool-first. Dieses Paket liefert die **Spezifikation, Rubrik, Templates und Tasks**, damit die Implementierung im Projekt-Repo sauber umgesetzt werden kann.

## Ergebnis-Artefakte (Standard)

Ausgabe-Orte (empfohlen):
- Manuskript (Quelle): `Docs/Documentation/<doc_name>.md`
- PDF: `Docs/References/<doc_name>.pdf`
- Diagramme (Quellen): `Docs/References/diagrams/<doc_name>/*.mmd` (oder `.dot`)
- Diagramme (Assets): `Docs/References/diagrams/<doc_name>/*.svg` (oder `.png`)

## Minimaler Workflow

1) **Explore**: Quellen sammeln, Zielgruppe/Scope klären, Outline bauen.
2) **Write**: Manuskript in einem Template erzeugen.
3) **Critic**: Rubrik anwenden, konkrete Fixliste (max 10 Items).
4) **DecideGap**: Quality Gap Report erzeugen (Score + „nächster großer Schritt“).
5) **Render**: `pdf_render` Skill ausführen.

Details: `skills/playbooks/pdf_quality_docforge.md`

## Templates

- `templates/lastenheft.template.md`
- `templates/first_steps.template.md`
- `templates/tutorial.template.md`
- `templates/api_reference.template.md`

## Deterministischer Skill

- Skill-ID: `pdf_render`
- Contract: `contracts/schemas/pdf_render_inputs.schema.json`
- Example Request: `contracts/examples/pdf_render.skill_request.example.json`

## Beispiele

Siehe `skills/pdf_quality/examples/`:
- `sample_lastenheft.md`
- `sample_first_steps.md`
- `sample_diagrams.mmd`
