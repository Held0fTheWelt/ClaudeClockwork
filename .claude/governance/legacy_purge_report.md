# Legacy Purge Report: `.oodle` Removal / Elimination

Policy: `.oodle` paths are obsolete (not deprecated). This repo must not reference `.oodle/` anywhere.

Changed files: **18**

- `.claude/CHANGELOG.md` — occurrences before: 3 / after: 0
- `.claude/agents/context_packer.md` — occurrences before: 2 / after: 0
- `.claude/agents/critic_dispatcher.md` — occurrences before: 2 / after: 0
- `.claude/agents/personaler.md` — occurrences before: 3 / after: 0
- `.claude/agents/task_compactor.md` — occurrences before: 1 / after: 0
- `.claude/agents/tester.md` — occurrences before: 2 / after: 0
- `.claude/agents/workers/report_worker.md` — occurrences before: 1 / after: 0
- `.claude/governance/file_ownership.md` — occurrences before: 1 / after: 0
- `.claude/governance/path_semantics.md` — occurrences before: 2 / after: 0
- `.claude/governance/qa_gate_policy.md` — occurrences before: 1 / after: 0
- `.claude/knowledge/decisions.md` — occurrences before: 2 / after: 0
- `.claude/tools/skills/doc_ssot_resolver.py` — occurrences before: 3 / after: 0
- `.claude/tools/skills/code_clean_scan.py` — occurrences before: 1 / after: 0
- `.claude/skills/registry.md` — occurrences before: 1 / after: 0
- `.claude/skills/code_clean/README.md` — occurrences before: 1 / after: 0
- `.claude/changelog/release_notes/v17_3.md` — occurrences before: 1 / after: 0
- `.claude/changelog/release_notes/v17_5.md` — occurrences before: 1 / after: 0
- `.claude/changelog/release_notes/v17_6.md` — occurrences before: 1 / after: 0

If you still see `.oodle` references, run `hardening_scan_fix` with scenario `purge_oodle_refs`.
