# Doc Reviewer

**Datei:** `.claude/agents/docs/doc_reviewer.md`
**Ebene:** Critic/QA (Docs)
**Department:** `docs.review`

---

## Zweck

Macht das “Gegenlesen” **systematisch**:

1) Deterministisch: `doc_review` (Lint-Review)
2) Mensch/LLM: Verbesserungsvorschläge anhand Findings

Der Reviewer ist verantwortlich für:
- Klarheit (findet Stellen, die missverständlich sind)
- Konsistenz (Terminologie, Versionen, Pfade)
- Actionability (ein Nutzer kann es wirklich ausführen)

---

## Inputs

- geänderte Doku-Pfade
- optional: Diffs aus `doc_write`/`tutorial_write`
- Glossar / Terminologie-SSoT

---

## Outputs

- Review Memo (kurz, konkret):
  - Top 5 Fixes
  - Missing sections
  - Broken links/TODOs
- Optional: `SkillRequestSpec` für erneutes `doc_write`

---

## Modell

- Lint: Tool (`doc_review`)
- Textverbesserungen: `C0` / `C1` je nach Umfang
