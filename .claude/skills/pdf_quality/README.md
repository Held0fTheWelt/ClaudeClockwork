# Skill: NanoBanana PDF Quality (DocForge)

Goal: From existing project documents (Specs/Runbooks/Tasks/Notes), produce **readable, print-ready PDFs** with **appropriate diagrams and schemas**.

This skill pack is designed for **Claude Clockwork**:
- **LLM part (non-deterministic):** Explore/Write/Critic/DecideGap generate `manuscript.md` + diagram sources.
- **Tool part (deterministic):** `pdf_render` renders a PDF from the manuscript + diagram assets.

> Important: In Clockwork, skills are tool-first. This package provides the **specification, rubric, templates, and tasks** so that implementation in the project repo can be done cleanly.

## Output Artifacts (Standard)

Output locations (recommended):
- Manuscript (source): `Docs/Documentation/<doc_name>.md`
- PDF: `Docs/References/<doc_name>.pdf`
- Diagrams (sources): `Docs/References/diagrams/<doc_name>/*.mmd` (or `.dot`)
- Diagrams (assets): `Docs/References/diagrams/<doc_name>/*.svg` (or `.png`)

## Minimal Workflow

1) **Explore**: Collect sources, clarify audience/scope, build outline.
2) **Write**: Generate manuscript using a template.
3) **Critic**: Apply rubric, produce concrete fix list (max 10 items).
4) **DecideGap**: Generate Quality Gap Report (Score + "next major step").
5) **Render**: Execute `pdf_render` skill.

Details: `skills/playbooks/pdf_quality_docforge.md`

## Templates

- `templates/lastenheft.template.md`
- `templates/first_steps.template.md`
- `templates/tutorial.template.md`
- `templates/api_reference.template.md`

## Deterministic Skill

- Skill ID: `pdf_render`
- Contract: `contracts/schemas/pdf_render_inputs.schema.json`
- Example Request: `contracts/examples/pdf_render.skill_request.example.json`

## Examples

See `skills/pdf_quality/examples/`:
- `sample_lastenheft.md`
- `sample_first_steps.md`
- `sample_diagrams.mmd`
