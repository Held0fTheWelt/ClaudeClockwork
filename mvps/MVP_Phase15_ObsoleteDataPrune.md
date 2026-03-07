# MVP Phase 15 — Obsolete Data Prune

**Goal:** Systematically identify and permanently remove files that have lost their context — replaced files, superseded documentation, orphaned reference artifacts, dead pointer files, and any file whose purpose can no longer be traced to an active system function. Establishes the `file_lifecycle` governance rule to prevent re-accumulation.

**Source finding:** User directive — "make a rule to never ever let files exist that lost their context to the system, or have been replaced by others somehow."

**Principle:** A file with no active reader, no active reference, and no clear system purpose is not "archived" — it is deleted. Ambiguous files are resolved by decision, not by accumulation.

---

## Definition of Done

- [ ] Full scan of repo completed: every file classified as `active`, `superseded`, or `orphaned`
- [ ] All `superseded` files deleted or explicitly converted to pointer stubs
- [ ] All `orphaned` files deleted (no exceptions without explicit justification recorded in `CLAUDE.md`)
- [ ] `.claude/governance/file_lifecycle.md` created — the permanent rule preventing re-accumulation
- [ ] `dead_file_scan` skill created — manifest-registered skill that automates future orphan detection
- [ ] `tests/test_dead_file_scan.py` — 6 tests verifying scan behavior
- [ ] Roadmap updated: Phase 15 = this phase; Phase 16 = Skill Discovery Wave

---

## P15.1 — Prune Scan

**What to scan:**

| Location | Orphan signal |
|----------|--------------|
| `Docs/` (root) | Superseded by `.project/Docs/`; contents already migrated in Phase 11 |
| `mvps/archive/MVP_Chain_Legacy.md` | Check if any sections are still live or all content is indexed |
| `roadmaps/archive/` | Verify every file is a pointer stub, not a live document |
| `.claude-development/` | Verify ARCHIVED header is present; no file has a live CLAUDE.md reference |
| Root-level stale files | `NEW_MVPS.md`, `VERIFY.md`, `SRC_ORIGIN_RULE.md` — verify if superseded |
| `.claude/governance/deep_oodle_mode.md` | Oodle naming is retired; verify if entire file is stale |
| `.claude/governance/no_llm_mode.md` | Check if still referenced or purely historical |
| `validation_runs/` | Transient outputs — delete all contents (keep directory); never commit |
| `skill_system_audit_and_roadmap (1).md` | Duplicate filename with space; must be removed |
| `skill_system_legacy_migration_matrix.csv` | Root-level duplicate of `Docs/` version |
| `skill_system_legacy_migration_matrix.md` | Root-level duplicate of `Docs/` version |

**Decision rule:** A file is `orphaned` if ALL of the following are true:
1. No other file in the repo references it (no backlinks)
2. No active agent or governance doc names it as authoritative
3. Its content is either empty, a pointer to another file, or a verbatim duplicate

---

## P15.2 — `dead_file_scan` Skill

**Native location:** `.claude/skills/meta/dead_file_scan/skill.py` (native SkillBase)
**Manifest package:** `.claude/skills/meta/dead_file_scan/`

**Logic:** Walk the repo and classify files against the file lifecycle rules in `.claude/governance/file_lifecycle.md`. Return a structured list of candidates for deletion.

**Detection heuristics:**
- **Superseded:** file contains a `<!-- SUPERSEDED` or `> ARCHIVED` header comment (added by previous migration phases)
- **Duplicate content:** SHA256 of content matches another file in the repo exactly
- **Orphaned pointer:** file is ≤ 5 lines and its only content is a `→` reference to another file, but the source file is not referenced anywhere else
- **Dead reference:** file references paths that no longer exist in the repo (>50% of its own path references are broken)

**Inputs:**
- `root` (str, optional — defaults to working directory)
- `scan_paths` (list of str, optional — defaults to `["Docs/", "roadmaps/", "mvps/", ".claude-development/"]`)
- `dry_run` (bool, optional, default true — never deletes; always returns candidates only)

**Outputs:**
- `candidates` (list of `{path, reason, confidence}` — confidence: `"high"` | `"medium"` | `"low"`)
- `candidate_count` (int)
- `high_confidence_count` (int)

**Permissions:** `["repo:read"]`

**Important:** This skill NEVER deletes files. It only reports. Deletion requires human confirmation.

---

## P15.3 — `file_lifecycle` Governance Rule

**File:** `.claude/governance/file_lifecycle.md`

This is the permanent rule that prevents future accumulation of orphaned files. See the full content in the created file.

---

## P15.4 — Tests (`tests/test_dead_file_scan.py`)

6 tests:

1. `test_dead_file_scan_in_registry` — skill is in the registry
2. `test_dead_file_scan_is_native` — not a LegacySkillAdapter
3. `test_dead_file_scan_dry_run_only` — verify `dry_run=false` is rejected (safety guard)
4. `test_dead_file_scan_returns_candidates` — returns `candidates` list with required keys
5. `test_dead_file_scan_confidence_values` — all candidates have `"high"` | `"medium"` | `"low"` confidence
6. `test_dead_file_scan_no_false_positive_on_active_files` — active governance files (e.g., `CLAUDE.md`, `execution_protocol.md`) are never flagged

---

## Files Changed

| File | Change |
|------|--------|
| `mvps/MVP_Phase15_ObsoleteDataPrune.md` | This file — new Phase 15 |
| `mvps/MVP_Phase16_SkillDiscovery.md` | Renumbered from Phase 15 |
| `mvps/MVP_Phase15_SkillDiscovery.md` | Redirected → pointer to Phase 16 |
| `roadmaps/Roadmap_ClockworkV18.md` | Phase table updated |
| `.claude/governance/file_lifecycle.md` | New governance rule |
| `.claude/skills/meta/dead_file_scan/manifest.json` | New skill manifest |
| `.claude/skills/meta/dead_file_scan/skill.py` | New native skill |
| `.claude/skills/meta/dead_file_scan/__init__.py` | New (empty) |
| `tests/test_dead_file_scan.py` | New — 6 tests |
| Root-level duplicate files | Deleted (see P15.1 scan) |
| `validation_runs/` contents | Deleted (transient outputs) |

---

## Dependencies

- Phase 14 complete — native skill pattern established
- No code dependencies — this phase is primarily a governance + cleanup operation

## Acceptance Criteria

- `dead_file_scan` skill exists in registry and returns `status: ok` in dry_run mode
- `.claude/governance/file_lifecycle.md` exists and is referenced from `CLAUDE.md`
- All root-level duplicate files identified in P15.1 are deleted
- 6 tests in `tests/test_dead_file_scan.py` pass
- `git diff --name-only` after pruning shows only deleted files (no modifications to live content)
- All pre-existing tests continue to pass
