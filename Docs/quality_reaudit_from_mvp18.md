# Quality Re-Audit from MVP 18 — Baseline Report

**Date:** 2026-03-07
**Scope:** Gates for MVP 18 and onward
**Status:** FAIL (5 blockers, 7 passing)

---

## Executive Summary

Re-audit of quality gates performed at the start of MVP 18 (the release candidate cycle). **5 blocking gates failed**, each mapped to a dedicated fix MVP (18G–18J). All failures are addressable through focused, incremental work.

---

## Gate Results

| Check ID | Gate Name | Status | Severity | Fix MVP |
|-----------|-----------|--------|----------|---------|
| BOOT_001 | boot_check passes | PASS | — | — |
| LAYOUT_001 | required dirs exist | PASS | — | — |
| SCHEMA_001 | contracts parse as JSON | PASS | — | — |
| SKILL_001 | registry.md vs .py count | PASS | — | — |
| POLICY_001 | hardlines.yaml valid YAML | PASS | — | — |
| ADDON_001 | addon skill implementations | PASS | — | — |
| AGENT_001 | agent registry ratio | SKIP | — | — |
| **REPORT_001** | **.report/ has README.md** | **FAIL** | **BLOCKER** | **18H** |
| **POINTER_001** | **.claude/ has pointer docs** | **FAIL** | **BLOCKER** | **18G** |
| **VERSION_001** | **.claude/VERSION is semver** | PASS | — | — |
| POINTER_002 | pointer file refs resolve | SKIP | — | — |
| **COVERAGE_001** | **skill dispatch coverage** | **FAIL** | **BLOCKER** | **18I** |
| **DRIFT_001** | **planning drift scan** | **FAIL** | **BLOCKER** | *18G or 18F* |
| **RELEASE_001** | **release check** | **FAIL** | **BLOCKER** | *18F or later* |

**Pass Rate:** 7/14 (50%)
**Blocker Count:** 5

---

## Failure Details

### REPORT_001 — Missing `.report/README.md`

**Message:** `missing: .report/README.md`
**Severity:** BLOCKER
**Fix MVP:** 18H
**Action:**
- Create `.report/README.md` documenting curated-only report policy
- Ensure `.report/` contains only human-reviewed markdown summaries
- Move transient/machine-generated outputs to `.clockwork_runtime/`

---

### POINTER_001 — Missing `.claude/` Pointer Documents

**Message:** `missing pointer targets: .claude/ARCHITECTURE.md, .claude/ROADMAP.md, .claude/MODEL_POLICY.md`
**Severity:** BLOCKER
**Fix MVP:** 18G
**Action:**
- Create `.claude/ARCHITECTURE.md` → pointer to `ARCHITECTURE.md`
- Create `.claude/ROADMAP.md` → pointer to `ROADMAP.md`
- Create `.claude/MODEL_POLICY.md` → pointer to `MODEL_POLICY.md`

**Rationale:** Deployable unit is `.claude/`, so all essential docs must be reachable within it.

---

### COVERAGE_001 — Missing Skill Dispatch Entry

**Message:** `non-stub skill(s) in registry.md have no dispatch entry in skill_runner.py: clockwork_changelog_entry`
**Severity:** BLOCKER
**Fix MVP:** 18I
**Action:**
- Implement `.claude/tools/skills/clockwork_changelog_entry.py`
- Register skill in `.claude/tools/skills/skill_runner.py` SKILLS dict
- Verify skill returns `status == "ok"`

**Rationale:** `clockwork_changelog_entry` is listed in registry.md but has no implementation or dispatch entry.

---

### DRIFT_001 — Planning Drift Scan Unavailable

**Message:** `planning_drift_scan unavailable (claudeclockwork.core.gates not importable)`
**Severity:** BLOCKER
**Fix MVP:** 18G (version consistency) or 18F (gate import)
**Action:**
1. Ensure `claudeclockwork.core.gates` module exists and is importable
2. Verify version file drift is resolved (ROOT `VERSION` vs `.claude/VERSION`)
3. Re-run gate after 18G to confirm

**Known Issue:** Root `VERSION` = 17.7.87, `.claude/VERSION` = 17.7.165 (version drift detected).

---

### RELEASE_001 — Release Check Unavailable

**Message:** `run_release_check unavailable (claudeclockwork.core.gates not importable)`
**Severity:** BLOCKER
**Fix MVP:** 18F/18G (once gates are importable), or 18J (final green run)
**Action:**
1. Resolve DRIFT_001 issue (gates module import)
2. Ensure changelog entry for current version exists (Phase 22 requirement)
3. Re-run gate after 18G

---

## Green Criteria (RC Minimum)

For a "Green Run" release candidate, the following gates must pass:

1. **BOOT_001** — Environment health check
2. **LAYOUT_001** — Required project structure
3. **SCHEMA_001** — Contract schemas valid
4. **REPORT_001** — Curated report structure
5. **POINTER_001** — `.claude/` pointer docs
6. **VERSION_001** — Version file present and valid semver
7. **COVERAGE_001** — Skill dispatch coverage ≥90%
8. **DRIFT_001** — Planning drift scan passes
9. **RELEASE_001** — Release check passes

**Status:** Currently 4/9 green, 5 blockers preventing release.

---

## Recommended Next Steps

1. **18F (This phase):** Ensure qa_gate is runnable deterministically (DONE)
2. **18G:** Fix version drift + create `.claude/` pointer docs → unblocks POINTER_001, may unblock DRIFT_001
3. **18H:** Create `.report/README.md` → unblocks REPORT_001
4. **18I:** Implement `clockwork_changelog_entry` → unblocks COVERAGE_001
5. **18J:** Run final green run, generate certificate

---

## Historical Context

This re-audit supersedes all previous audit snapshots. It is the baseline for MVP 18 onward and is reproducible via:

```bash
python3 .claude/tools/skills/qa_gate.py '{"skill_id":"qa_gate","inputs":{"project_root":".","write_report":false}}'
```

Results are stable-ordered and deterministic (except timestamps if included).
