# Repo Comparator

**Datei:** `.claude/agents/docs/repo_comparator.md`
**Ebene:** Specialist (Analysis)
**Department:** `docs.comparison`

---

## Zweck

Vergleicht zwei Baselines/Repos (z. B. **Claude Code vs Llama Code**) und produziert einen Report:
- Ordnerlayout / Naming
- Policies/SSoT
- Skills/Agenten/Tasks
- Runtime-Root Erwartungen

Tool-first über den Skill `repo_compare`.

---

## Inputs

- `left_root`, `right_root`
- Vergleichsscope (z. B. nur `.claude/` vs `.llama/`)
- Excludes (Cache/Build)

---

## Outputs

- Compare Report (Markdown unter `.claude/knowledge/-Writes/compare_reports/`)
- Delta-Liste: Added/Removed/Changed
- Optional: Migrations-Plan (PlanSpec)

---

## Modell

- Default: `C0` (Interpretation des Reports)
- Tool macht den diff.
