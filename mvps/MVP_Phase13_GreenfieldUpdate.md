# MVP Phase 13 — Greenfield Update: Stale Package Reference Cleanup

**Goal:** Eliminate all remaining references to the stale `llamacode/`, `oodle/`, and `src/` package names from documentation and stub files. Rewrite `.claude/docs/` stub files to accurately describe the current `claudeclockwork/` package. After this phase, no documentation in `.claude/` references a package or path that does not exist.

**Source finding:** NEW_MVPS.md — "Make it modern and matching to the Anthropic [standards]". VERIFY 2026-03-06 C1 residual.

**Key stale files identified:**
- `.claude/docs/ARCHITECTURE_STUB.md` — references `llamacode/` package layout, `oodle` CLI
- `.claude/docs/API_STUB.md` — references `oodle` CLI commands, `llamacode/cli.py`
- `.claude/development/MVP_STATUS.md` — references `llamacode/core/` paths throughout
- `.claude/skills/escalation_router.md` — references `llamacode/core/escalation_router.py`
- `.claude/skills/registry.md` — entries reference `llamacode/core/`

---

## Definition of Done

- [ ] `.claude/docs/ARCHITECTURE_STUB.md` rewritten: `llamacode/` replaced with `claudeclockwork/`, `oodle` CLI replaced with `python -m claudeclockwork.cli`
- [ ] `.claude/docs/API_STUB.md` rewritten: all `oodle`/`llamacode` references replaced with `claudeclockwork` equivalents
- [ ] `.claude/development/MVP_STATUS.md` updated: `llamacode/core/*` paths updated or annotated as "implemented in `claudeclockwork/`"
- [ ] `.claude/skills/escalation_router.md` updated: `llamacode/core/escalation_router.py` reference removed; replaced with accurate implementation note
- [ ] `.claude/skills/registry.md` updated: stale `llamacode/` references removed or corrected to `claudeclockwork/core/`
- [ ] `grep -r "llamacode\|oodle_tier\|from oodle" .claude/docs/ .claude/development/ .claude/skills/` returns zero results in these specific subdirectories (historical references in `.claude-development/` are excluded — those are an archived read-only record)
- [ ] All existing tests pass

---

## P13.1 — Rewrite `.claude/docs/ARCHITECTURE_STUB.md`

**Finding:** Current content describes `llamacode/` as the primary package with `oodle` as the CLI entry point. This is the pre-migration layout. The package was renamed to `claudeclockwork/` and the CLI entry point is now `python -m claudeclockwork.cli`.

**Rewrite requirements:**
- Title: "Architecture Overview (Stub)" — keep the stub designation; full detail is in root `ARCHITECTURE.md`
- Primary package: `claudeclockwork/`
- Entry point: `python -m claudeclockwork.cli`
- Key modules to document:
  - `claudeclockwork/cli.py` — CLI entry point and argument parsing
  - `claudeclockwork/runtime.py` — registry builder and runtime bootstrap
  - `claudeclockwork/bridge.py` — manifest bridge / `LegacySkillAdapter`
  - `claudeclockwork/core/registry/` — skill discovery and loading
  - `claudeclockwork/core/executor/` — execution pipeline
  - `claudeclockwork/core/planner/` — planning and routing
  - `claudeclockwork/core/security/` — security validation
- Add footer note: "This is a stub — see root `ARCHITECTURE.md` for the full system architecture."
- Remove all occurrences of `llamacode`, `oodle`, and `src/` as package or directory names

**Validation:**
```bash
grep -i "llamacode\|oodle\|from src" .claude/docs/ARCHITECTURE_STUB.md && echo STALE || echo PASS
grep -c "claudeclockwork" .claude/docs/ARCHITECTURE_STUB.md  # must be > 0
```

**Acceptance:** Zero occurrences of `llamacode` or `oodle` in the file. String `claudeclockwork` appears as the primary package name.

---

## P13.2 — Rewrite `.claude/docs/API_STUB.md`

**Finding:** Current content documents `oodle <command>` CLI syntax and `llamacode/cli.py` as the entry point. The actual CLI is invoked as `python -m claudeclockwork.cli` with `--skill-id`, `--inputs`, and related flags.

**Rewrite requirements:**
Document the actual `claudeclockwork.cli` interface currently implemented:

```
python -m claudeclockwork.cli --skill-id <skill_name> --inputs '{...}'
python -m claudeclockwork.cli --skill-id <skill_name> --inputs '{}' --dry-run
python -m claudeclockwork.cli --list-skills
python -m claudeclockwork.cli --plugin-healthcheck <plugin_name>
python -m claudeclockwork.mcp  # MCP STDIO server
```

Include:
- A brief description of each flag
- A note on input format: `--inputs` accepts a JSON string
- A note distinguishing the two dispatch paths (manifest CLI vs legacy runner) — reference `CLAUDE.md` "Skill Dispatch" section for full detail
- Remove all `oodle`, `llamacode`, and `src/` references

**Validation:**
```bash
grep -i "llamacode\|oodle\| oodle" .claude/docs/API_STUB.md && echo STALE || echo PASS
grep "claudeclockwork.cli" .claude/docs/API_STUB.md  # must return a match
```

**Acceptance:** Zero occurrences of `llamacode` or `oodle` in the file. String `python -m claudeclockwork.cli` appears as the canonical CLI invocation.

---

## P13.3 — Update `.claude/development/MVP_STATUS.md`

**Finding:** `MVP_STATUS.md` tracks completion status for each MVP phase. Several entries reference `llamacode/core/X.py` as the implementation path — these paths no longer exist. Some of the referenced modules were migrated to `claudeclockwork/core/`; others are planned for Phase 3 (Native Core Services).

**Steps:**
1. Read `.claude/development/MVP_STATUS.md` in full
2. For each entry referencing `llamacode/core/<module>.py`:
   - If the module exists at `claudeclockwork/core/<module>`, update the path to `claudeclockwork/core/<module>`
   - If the module has not yet been migrated, append a note: `(core implementation planned — Phase 3: Native Core Services)`
3. Do not alter MVP completion status markers (`[X]`, `[ ]`, `DONE`, etc.)
4. Do not alter the structure, ordering, or wording of any MVP entry beyond the path corrections and Phase 3 annotations

**Validation:**
```bash
grep -c "llamacode/core" .claude/development/MVP_STATUS.md  # must be 0
```

**Acceptance:** Zero occurrences of `llamacode/core` in the file. All path references use `claudeclockwork/core/` or carry an explicit Phase 3 annotation.

---

## P13.4 — Update `.claude/skills/escalation_router.md`

**Finding:** The skill documentation contains an import stub referencing the pre-migration package:
```
from llamacode.core.escalation_router import EscalationRouter, AllRungsExhausted
Implementation: llamacode/core/escalation_router.py
```
The `llamacode` package no longer exists. The legacy skill wrapper is at `.claude/tools/skills/escalation_router.py`. The native `claudeclockwork` implementation is not yet complete and is scoped to Phase 3.

**Change:** Replace the stale import stub and implementation path with an accurate implementation note:
```
# Implementation note
The active skill implementation is the legacy wrapper:
  .claude/tools/skills/escalation_router.py

A native claudeclockwork implementation is planned for Phase 3 (Native Core Services).
The legacy wrapper does not import from llamacode — that dependency was removed in Phase 8 (H8.2).
```

**Validation:**
```bash
grep "llamacode" .claude/skills/escalation_router.md && echo STALE || echo PASS
```

**Acceptance:** Zero occurrences of `llamacode` in the file. The implementation note correctly describes the legacy wrapper location and Phase 3 plan.

---

## P13.5 — Update `.claude/skills/registry.md`

**Finding:** `registry.md` contains skill registry entries that reference `llamacode/core/` as the implementation path. These entries misdirect agents to a non-existent package.

**Steps:**
1. Read `.claude/skills/registry.md` in full
2. For each registry entry containing `llamacode/core/`:
   - If the corresponding module exists in `claudeclockwork/core/`, update the path
   - If the module has not been migrated, update the path to the legacy wrapper location (`.claude/tools/skills/<skill>.py`) and add a note: `(claudeclockwork native: planned Phase 3)`
3. Specifically update the `escalation_router` entry: remove the `llamacode/` reference; point to `.claude/tools/skills/escalation_router.py`
4. Confirm no entry contains `llamacode/core` after the update

**Validation:**
```bash
grep "llamacode" .claude/skills/registry.md && echo STALE || echo PASS
```

**Acceptance:** Zero occurrences of `llamacode` in the file. All entries reference either `claudeclockwork/core/` or the correct legacy wrapper path.

---

## P13.6 — Scan and clean `.claude/docs/glossary.md`

**Finding:** The glossary may contain entries defining `llamacode` or `oodle` as active system terms. These need to be updated or marked as retired terminology.

**Steps:**
1. Run: `grep -in "llamacode\|oodle" .claude/docs/glossary.md`
2. For each matching entry:
   - If it defines `llamacode` as the package name: update to `claudeclockwork` and add a note: "(formerly llamacode — renamed during Clockwork v18 greenfield update)"
   - If it defines `oodle` as the CLI: update to `python -m claudeclockwork.cli` and add a note: "(formerly oodle CLI — removed in Clockwork v18)"
   - If the entry is a historical note only, prefix with: "**Retired:** " and leave the rest unchanged for archival context
3. If `.claude/docs/glossary.md` does not exist, skip this task and record "P13.6 — N/A: glossary.md not present" in the MVP status update

**Validation:**
```bash
grep -i "llamacode\|oodle" .claude/docs/glossary.md | grep -v "formerly\|Retired" && echo STALE || echo PASS
```

**Acceptance:** No occurrence of `llamacode` or `oodle` in glossary.md refers to an active current system component without a "formerly" or "Retired" qualifier.

---

## Files Changed

| File | Change |
|------|--------|
| `.claude/docs/ARCHITECTURE_STUB.md` | Full rewrite: `llamacode` → `claudeclockwork`, `oodle` CLI → `python -m claudeclockwork.cli` |
| `.claude/docs/API_STUB.md` | Full rewrite: `oodle`/`llamacode` → `claudeclockwork.cli` interface |
| `.claude/development/MVP_STATUS.md` | Update `llamacode/core/` path references to `claudeclockwork/core/` or Phase 3 annotations |
| `.claude/skills/escalation_router.md` | Remove `llamacode` import stub; replace with accurate implementation note |
| `.claude/skills/registry.md` | Remove/update all `llamacode/core/` references |
| `.claude/docs/glossary.md` | Update stale `llamacode`/`oodle` entries; mark retired terminology |

---

## Acceptance Criteria

- `grep -r "from llamacode\|llamacode/" .claude/docs/ .claude/development/ .claude/skills/` returns zero results
- `grep -r "oodle_tier\|from oodle\| oodle " .claude/docs/ .claude/development/ .claude/skills/` returns zero results
- `.claude/docs/ARCHITECTURE_STUB.md` contains `claudeclockwork` as the primary package name
- `.claude/docs/API_STUB.md` contains `python -m claudeclockwork.cli` as the canonical CLI invocation
- `.claude/development/MVP_STATUS.md` contains zero occurrences of `llamacode/core`
- `.claude/skills/escalation_router.md` contains zero occurrences of `llamacode`
- `.claude/skills/registry.md` contains zero occurrences of `llamacode`
- All existing tests pass
