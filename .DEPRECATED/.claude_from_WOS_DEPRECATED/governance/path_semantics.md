# Path Semantics (Canonical)

To prevent drift and broken references:

## Rule
All file paths written in backticks (e.g. `contracts/schemas/...`) are interpreted as **.claude-root-relative** paths,
unless explicitly prefixed with:
- `<PROJECT_ROOT>/...` (project repo root)
- `validation_runs/...` (evidence folder root)

## Examples
- `governance/feedback_policy.md` means `.claude/governance/feedback_policy.md`
- `<PROJECT_ROOT>/src/...` means project root path

## Why
This removes ambiguity between "file-relative" and "repo-relative" references.

## Legacy compatibility
Some older documents use:
- `.claude/...` or `.claude/...` (repo-root-relative)
- filename-only refs like `execution_protocol.md`

Tools like `doc_ssot_resolver` resolve these forms for backwards compatibility.
Preferred style for new docs remains `.claude`-root-relative paths like `governance/execution_protocol.md`.

## SSoT validation scope
`doc_ssot_resolver` (and therefore `qa_gate`) can run in two modes:

- Default (**claude_only**): validates only references that can be resolved inside `.claude/`.
  `<PROJECT_ROOT>/...` references are treated as *external* and skipped, **except** `<PROJECT_ROOT>/.claude/...` which is always checked.
- Full (**project**): set `verify_project_root=true` (or `ssot_scope=full`) to also validate `<PROJECT_ROOT>/...` references.

Legacy `.claude/...` references are skipped unless `verify_legacy=true`.
