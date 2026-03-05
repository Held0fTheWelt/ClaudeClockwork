# Documentation Skills — Operational Reference

_Last updated: 2026-03-02 (CCW-MVP04)_

All doc skills are deterministic and invoked via:
```bash
python3 .claude/tools/skills/skill_runner.py --in <input.json> --out <result.json>
```

The `skill` field in the input JSON selects which skill to run.

---

## doc_write (skill #39)

**Skill ID:** `doc_write`
**Purpose:** Deterministic documentation file writer. Writes one or many Markdown
files from prepared content and produces a unified diff for review. Blocks path
traversal (stays inside `project_root`).
**Input:** `DocWriteRequest` — list of file entries (path + content), project_root.
**Output:** `DocWriteResult` — files written, unified diff, errors.
**Tool:** `.claude/tools/skills/doc_write.py`

---

## doc_review (skill #41)

**Skill ID:** `doc_review`
**Purpose:** Deterministic doc lint review. Checks for TODO/TBD leftovers, missing
required sections (tutorial/user guide/architecture/security), basic broken local
links, code fence language tag hints, and heading level jumps.
**Input:** `DocReviewRequest` — path(s) to Markdown files to review.
**Output:** `DocReviewResult` — issues list (severity, location, message), summary.
**Tool:** `.claude/tools/skills/doc_review.py`

---

## tutorial_write (skill #40)

**Skill ID:** `tutorial_write`
**Purpose:** Deterministic tutorial renderer. Accepts a structured `tutorial_spec`
or ready-made Markdown, validates required tutorial sections (goal, prereqs, steps,
summary), emits warnings for missing sections, writes via `doc_write`, returns diff.
**Input:** `TutorialWriteRequest` — tutorial_spec or raw_markdown, output path.
**Output:** `TutorialWriteResult` — files written, warnings, unified diff.
**Tool:** `.claude/tools/skills/tutorial_write.py`

---

## doc_ssot_resolver (skill #28)

**Skill ID:** `doc_ssot_resolver`
**Purpose:** Resolves backtick path references inside `.claude/` documents using
Path Semantics rules. Reports missing targets (files that are referenced but do
not exist). Used during `qa_gate` to catch documentation drift.
**Input:** `DocSsotResolverRequest` — root path(s) to scan, optional strict mode.
**Output:** `DocSsotResolverResult` — missing references list, resolved count.
**Tool:** `.claude/tools/skills/doc_ssot_resolver.py`

---

## autodocs_generate (skill #61)

**Skill ID:** `autodocs_generate`
**Purpose:** Deterministic per-skill documentation generator. Creates or updates
`skills/<skill_id>/README.md` for each tool under `.claude/tools/skills/`. Classifies
skills as core vs addon using `addons/map.yaml`. Reduces skills-registry drift.
**Input:** `AutodocsGenerateRequest` — tools dir, skills dir, optional filter list.
**Output:** `AutodocsGenerateResult` — files written/updated, skipped, diff.
**Tool:** `.claude/tools/skills/autodocs_generate.py`

---

## screencast_script (skill #43)

**Skill ID:** `screencast_script`
**Purpose:** Deterministic screencast script writer. Renders a chapter + shot list
script from a `script_spec` (title, audience, chapters with narration + on-screen
actions). Writes Markdown via `doc_write` and returns a unified diff.
**Input:** `ScreencastScriptRequest` — script_spec, output path.
**Output:** `ScreencastScriptResult` — files written, diff.
**Tool:** `.claude/tools/skills/screencast_script.py`

---

## pdf_render (skill #55)

**Skill ID:** `pdf_render`
**Purpose:** Renders a high-quality PDF from a prepared Markdown manuscript plus
optional diagram specs and style options. Fully deterministic — no LLM calls.
Falls back to HTML if pandoc/reportlab are unavailable.
**Input:** `PdfRenderRequest` — markdown (string or path), diagrams JSON, output pdf_path, style options.
**Output:** `PdfRenderResult` — pdf_path, render_warnings.
**Tool:** `.claude/tools/skills/pdf_render.py`
**Templates/rubric:** `.claude/skills/pdf_quality/` (DocForge pack)

---

## Related playbooks

| Playbook                                           | When to use                                 |
|----------------------------------------------------|---------------------------------------------|
| `.claude/skills/playbooks/documentation_pipeline.md` | End-to-end doc write + review flow        |
| `.claude/skills/playbooks/pdf_quality_docforge.md`   | Explore → Write → Critic → Render for PDF |

---

_Full skill registry: `.claude/skills/registry.md`_
