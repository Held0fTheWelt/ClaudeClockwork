# MEMORY.md — Cross-Session Context

> Stable findings, architecture decisions, user preferences. SSoT for cross-session memory (Team Lead owned).
> See also: `.claude/knowledge/decisions.md` (append-only decision log).

---

## Stable Findings

- **Entrypoint namespace is correct.** `.claude` is added to `sys.path` by `SkillRegistry._ensure_import_paths()`. `.claude/skills/__init__.py` exists, making `skills.*` the correct import prefix for all manifests. All 34 skill classes load successfully.
- **Dual skill dispatch.** `skill_runner.py` (97 skills, direct dispatch) and `claudeclockwork.cli` (34 manifest skills via `LegacySkillAdapter`) are parallel systems with different coverage. 63 skills are only reachable via the legacy runner.
- **Plugin system is scaffolded only.** `plugins/` and `registry/` contain JSON metadata but zero Python loader code. Plugins cannot execute. Planned for Phase 4.
- **~170 files had German content** as of 2026-03-06. Root docs, SYSTEM.md, and agent/governance files were the highest-risk group (agents read these every session). Phase 0 translation is underway.

---

## Architecture Decisions

- `claudeclockwork/` is the canonical Python package (not `llamacode/`, `oodle/`, or `src/`). References to those names are stale and being removed.
- "Oodle Tier" renamed to "Local Model Tier" throughout docs and governance. Python variable names (`oodle_tier` in skill code) are deferred to Phase 3 as part of native rewrites.
- `.llama_runtime/` is the declared location for runtime state, eval results, and generated artifacts. Directory created in Phase 0; was missing before.
- `.report/` is the canonical location for human-facing reports. Directory created in Phase 0.
- Root `Docs/` (skill audit files) and `.project/Docs/` (plans/reviews/critics) are separate concerns. `.project/Docs/` is the SSoT per governance. Root `Docs/` holds audit artefacts — not actively referenced from governance.

---

## User Preferences

- **Project language:** English-only. All project-facing artifacts (code, manifests, docs, agent definitions, governance, skill READMEs) must be in English.
- **No big-bang rewrites.** Incremental phases: manifest hardening → wrapper waves → native rewrites → plugin runtime → MCP → CI gates.
- **Quality standard:** Run `qa_gate` + full test suite after each significant phase. Review output goes to `.project/Docs/Review/`.
- **Roadmap lives in `/roadmaps/`.** MVP descriptions live in `/mvps/`.

---

*Last updated: 2026-03-06 — Phase 0 (Foundation & Cleanup)*
