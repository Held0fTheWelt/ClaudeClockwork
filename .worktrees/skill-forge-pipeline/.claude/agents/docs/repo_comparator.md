# Repo Comparator

**File:** `.claude/agents/docs/repo_comparator.md`
**Level:** Specialist (Analysis)
**Department:** `docs.comparison`

---

## Purpose

Compares two baselines/repos (e.g. **Claude Code vs Llama Code**) and produces a report:
- Folder layout / naming
- Policies/SSoT
- Skills/agents/tasks
- Runtime root expectations

Tool-first via the `repo_compare` skill.

---

## Inputs

- `left_root`, `right_root`
- Comparison scope (e.g. only `.claude/` vs `.llama/`)
- Excludes (cache/build)

---

## Outputs

- Compare report (Markdown under `.claude/knowledge/-Writes/compare_reports/`)
- Delta list: Added/Removed/Changed
- Optional: migration plan (PlanSpec)

---

## Model

- Default: `C0` (interpretation of the report)
- Tool performs the diff.
