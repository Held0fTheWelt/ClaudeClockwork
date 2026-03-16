# Documentation Pipeline (v17.7)

This playbook describes a **repeatable** workflow to produce and maintain a complete software documentation set:
- **User documentation** (manual, FAQ, tutorials)
- **Technical documentation** (architecture, API/CLI docs, ops/admin)
- **Security** (guidelines + threat-model-light)
- **Release notes**
- **Screencast scripts** (storyboard + narration cues)
- **Glossary**
- **Diagrams** (spec-first: Mermaid/PlantUML)

The pipeline is designed to be:
- *tool-first* for persistence + linting (`doc_write`, `tutorial_write`, `doc_review`)
- reviewable via diffs
- compatible with QA (`repo_validate`, `qa_gate`)

---

## Roles (recommended)

- **Doc Orchestrator**: owns ToC, scope, and routing.
- **Doc Writer**: writes user/tech docs.
- **Tutorial Author**: produces step-by-step guides.
- **Doc Reviewer**: runs deterministic lint + issues a review memo.
- **Repo Comparator**: compares baselines (Claude Code ↔ Llama Code).

---

## Default target structure

```
Docs/
  Documentation/
    User_Guide.md
    FAQ.md
    Glossary.md
  Tutorials/
    01_Quickstart.md
    02_Advanced.md
  Tech/
    Architecture.md
    API_or_CLI.md
    Operations.md
  Security/
    Security_Guidelines.md
    Threat_Model_Light.md
  Release/
    Release_Notes.md
  Diagrams/
    c4_context.mmd
    sequence_flow.mmd
```

---

## Pipeline steps

### 1) Plan the doc set
- Define audiences (end user / admin / developer)
- Define scope (what is in/out)
- Freeze canonical naming + terminology (glossary baseline)

### 2) Draft content (agent/LLM)
- LLM drafts content in-memory.
- Keep it modular: one file per topic.

### 3) Persist via skills (tool-first)
- Write docs with `doc_write` (diff produced).
- Write tutorials with `tutorial_write` (section validation + diff).
- Write screencast scripts with `screencast_script` (shot list + diff).

### 4) Deterministic lint review
- Run `doc_review` on the updated docs folder.
- Fix structural issues (missing sections, broken links, TODOs).

### 5) Repo QA
- `repo_validate` (links/json)
- `qa_gate` (PR-blocking)

### 6) Compare baselines (optional)
- `repo_compare` to compare:
  - `.claude/` or `.llama/` structures
  - policies and skill sets
  - runtime root expectations

---

## Definition of Done (DoD)

- User guide includes: installation, basic usage, troubleshooting.
- Tutorials include: prerequisites, quickstart, walkthrough, verification, troubleshooting, next steps.
- Tech docs include: architecture components, data flow, ops/admin notes.
- Security docs include: threat model light + guidelines.
- Glossary covers all non-obvious terms.
- `doc_review` has **0 errors** and `repo_validate` passes.
