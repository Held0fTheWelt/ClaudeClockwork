# MVP Phase 12 — Duplicate Document Elimination

**Goal:** Eliminate the three-way document split for `ARCHITECTURE.md`, `ROADMAP.md`, `MODEL_POLICY.md`, `MEMORY.md`, and `QUALITY_TRACKING.md`. Each document must have exactly one canonical location. Pointers are permitted only where they add clear navigational value.

**Source finding:** NEW_MVPS.md — "duplicate files that only act as pointers should be eliminated. Additional information in files of the same type should be combined into one file only. References need to be updated."

**Resolution strategy:**
- Root files → project-level summary (what Clockwork is, how to use it) — keep as-is or simplify
- `.claude/` pointer files → DELETE (replace with real content or remove entirely; Claude Code reads `CLAUDE.md`, not `.claude/ARCHITECTURE.md`)
- `.project/` files → become canonical for Clockwork-dev cross-session operational data

---

## Definition of Done

- [ ] `.claude/ARCHITECTURE.md` pointer deleted; root `ARCHITECTURE.md` is the single architecture reference
- [ ] `.claude/ROADMAP.md` pointer deleted; root `ROADMAP.md` is the single roadmap reference
- [ ] `.claude/MODEL_POLICY.md` pointer deleted; content merged into root `MODEL_POLICY.md`; root is canonical
- [ ] `.claude/MEMORY.md` pointer deleted; `.project/MEMORY.md` is canonical; root `MEMORY.md` deleted (stub adds no value)
- [ ] `.claude/QUALITY_TRACKING.md` pointer deleted; `.project/QUALITY_TRACKING.md` is canonical; root `QUALITY_TRACKING.md` deleted (stub adds no value)
- [ ] `.claude/INDEX.md` updated — remove references to deleted pointer files
- [ ] `CLAUDE.md` updated — "Execution Protocol: read in this order" section updated to remove `.claude/` pointer files
- [ ] All existing tests pass

---

## P12.1 — ARCHITECTURE.md: delete `.claude/` pointer, keep root as canonical

**Finding:** Three copies exist: root `ARCHITECTURE.md` (25 lines, full doc), `.claude/ARCHITECTURE.md` (8-line pointer), `.project/ARCHITECTURE.md` (project-operational). Only one should survive. Root is the correct canonical — it is what external readers and Claude Code sessions see first.

**Steps:**
1. Read root `ARCHITECTURE.md`, `.claude/ARCHITECTURE.md`, and `.project/ARCHITECTURE.md`
2. Identify any unique content in `.project/ARCHITECTURE.md` not present in root
3. Merge unique content into root `ARCHITECTURE.md`
4. Delete `.claude/ARCHITECTURE.md`
5. Delete `.project/ARCHITECTURE.md` (or replace with a single-line pointer to root if a reference anchor is needed)
6. Search `.claude/INDEX.md` for any reference to `.claude/ARCHITECTURE.md` and remove the entry

**Validation:**
```bash
ls .claude/ARCHITECTURE.md 2>&1 && echo FAIL || echo PASS
ls .project/ARCHITECTURE.md 2>&1 && echo FAIL_or_pointer_only
grep -c "ARCHITECTURE" .claude/INDEX.md  # should be 0 or point to root only
```

**Acceptance:** `ls .claude/ARCHITECTURE.md` returns "No such file or directory". Root `ARCHITECTURE.md` contains all unique content previously in `.project/ARCHITECTURE.md`.

---

## P12.2 — ROADMAP.md: delete `.claude/` pointer, keep root as canonical

**Finding:** Root `ROADMAP.md` (23 lines) already contains version numbers and skill counts — it is the better canonical. `.claude/ROADMAP.md` is an 8-line pointer with no unique content.

**Steps:**
1. Read root `ROADMAP.md`, `.claude/ROADMAP.md`, and `.project/ROADMAP.md`
2. Identify any unique milestone or version content in `.project/ROADMAP.md` not in root
3. Merge unique content into root `ROADMAP.md`
4. Delete `.claude/ROADMAP.md`
5. Delete or simplify `.project/ROADMAP.md` (pointer to root if needed)
6. Update `.claude/INDEX.md` — remove `.claude/ROADMAP.md` reference

**Validation:**
```bash
ls .claude/ROADMAP.md 2>&1 && echo FAIL || echo PASS
```

**Acceptance:** `ls .claude/ROADMAP.md` returns "No such file or directory". Root `ROADMAP.md` is the sole roadmap document.

---

## P12.3 — MODEL_POLICY.md: merge content, delete `.claude/` pointer

**Finding:** Root `MODEL_POLICY.md` (17 lines) contains the full model tier table. `.claude/MODEL_POLICY.md` contains additional "conventions" and "performance budgeting" content not present in root. This unique content must be preserved via merge before the pointer is deleted.

**Steps:**
1. Read root `MODEL_POLICY.md` and `.claude/MODEL_POLICY.md` side by side
2. Identify sections in `.claude/MODEL_POLICY.md` that have no equivalent in root (e.g., conventions, performance budgeting notes)
3. Append unique sections to root `MODEL_POLICY.md` under clearly labelled headings
4. Delete `.claude/MODEL_POLICY.md`
5. Evaluate `.project/MODEL_POLICY.md` — if it contains only empty overrides (zero content), delete it; if it contains active overrides, keep as an override stub and add a comment header explaining its role
6. Update `.claude/INDEX.md` — remove `.claude/MODEL_POLICY.md` reference

**Validation:**
```bash
ls .claude/MODEL_POLICY.md 2>&1 && echo FAIL || echo PASS
grep -c "performance budgeting\|conventions" MODEL_POLICY.md  # should be > 0 if that content existed
```

**Acceptance:** `ls .claude/MODEL_POLICY.md` returns "No such file or directory". All unique content from the deleted pointer is present in root `MODEL_POLICY.md`.

---

## P12.4 — MEMORY.md: delete root stub, keep `.project/` as canonical

**Finding:** Root `MEMORY.md` is an 18-line stub with no cross-session content. `.project/MEMORY.md` (36 lines) is the real canonical used by Team Lead at session start. The stub at root adds confusion: it implies root is the memory location when it is not.

**Steps:**
1. Read root `MEMORY.md` — confirm it is a stub (no unique cross-session data)
2. Read `.project/MEMORY.md` — confirm it holds the real session memory
3. If root `MEMORY.md` has any unique content not in `.project/MEMORY.md`, migrate it
4. Delete root `MEMORY.md`
5. Delete `.claude/MEMORY.md` (pointer)
6. Update `CLAUDE.md` "Execution Protocol: read in this order" section:
   - Remove: `MEMORY.md` (root)
   - Confirm: `.project/MEMORY.md` is already listed, or add it

**Validation:**
```bash
ls MEMORY.md 2>&1 && echo FAIL || echo PASS
ls .claude/MEMORY.md 2>&1 && echo FAIL || echo PASS
grep "project/MEMORY" CLAUDE.md  # must return a match
```

**Acceptance:** `ls MEMORY.md` and `ls .claude/MEMORY.md` both return "No such file or directory". `CLAUDE.md` references `.project/MEMORY.md` in the read-order list.

---

## P12.5 — QUALITY_TRACKING.md: delete root stub, keep `.project/` as canonical

**Finding:** Root `QUALITY_TRACKING.md` is a 12-line minimal stub. `.project/QUALITY_TRACKING.md` (15 lines) is the active tracking document with telemetry and stats. Maintaining two copies creates confusion about where tracking data should be appended.

**Steps:**
1. Read root `QUALITY_TRACKING.md` — confirm it is a stub with no tracking data not in `.project/`
2. If root has any unique metrics rows, migrate them to `.project/QUALITY_TRACKING.md`
3. Delete root `QUALITY_TRACKING.md`
4. Delete `.claude/QUALITY_TRACKING.md` (pointer)
5. Update `CLAUDE.md` references — remove any mention of root `QUALITY_TRACKING.md`; reference `.project/QUALITY_TRACKING.md` if it appears in the read-order or governance notes

**Validation:**
```bash
ls QUALITY_TRACKING.md 2>&1 && echo FAIL || echo PASS
ls .claude/QUALITY_TRACKING.md 2>&1 && echo FAIL || echo PASS
```

**Acceptance:** Both `ls` commands return "No such file or directory". `.project/QUALITY_TRACKING.md` is the sole quality tracking document.

---

## P12.6 — Update INDEX.md and CLAUDE.md

**Finding:** `.claude/INDEX.md` lists the pointer files being deleted. `CLAUDE.md` "Execution Protocol" read-order may reference root `MEMORY.md` and root `QUALITY_TRACKING.md`.

**Steps:**
1. Read `.claude/INDEX.md` — identify all references to files being deleted in P12.1–P12.5
2. Remove each stale reference; replace with the canonical location where appropriate
3. Read `CLAUDE.md` — locate "Execution Protocol: read in this order" section
4. Update the read-order list to remove deleted files and confirm canonical paths are listed
5. Search `CLAUDE.md` for any other references to `.claude/ARCHITECTURE.md`, `.claude/ROADMAP.md`, `.claude/MODEL_POLICY.md`, `.claude/MEMORY.md`, `.claude/QUALITY_TRACKING.md` — remove or update each

**Validation:**
```bash
grep -E "\.claude/(ARCHITECTURE|ROADMAP|MODEL_POLICY|MEMORY|QUALITY_TRACKING)\.md" CLAUDE.md && echo STALE || echo PASS
grep -E "\.claude/(ARCHITECTURE|ROADMAP|MODEL_POLICY|MEMORY|QUALITY_TRACKING)\.md" .claude/INDEX.md && echo STALE || echo PASS
```

**Acceptance:** Both grep commands return zero results.

---

## Files Changed

| File | Change |
|------|--------|
| `ARCHITECTURE.md` | Merge in unique `.project/` content; becomes sole canonical |
| `.claude/ARCHITECTURE.md` | Deleted |
| `.project/ARCHITECTURE.md` | Deleted or converted to one-liner pointer to root |
| `ROADMAP.md` | Becomes sole canonical |
| `.claude/ROADMAP.md` | Deleted |
| `.project/ROADMAP.md` | Deleted or pointer |
| `MODEL_POLICY.md` | Merge `.claude/` conventions content; becomes sole canonical |
| `.claude/MODEL_POLICY.md` | Deleted |
| `.project/MODEL_POLICY.md` | Keep as override stub (zero content = no overrides) or delete |
| `MEMORY.md` | Deleted (root stub) |
| `.claude/MEMORY.md` | Deleted |
| `QUALITY_TRACKING.md` | Deleted (root stub) |
| `.claude/QUALITY_TRACKING.md` | Deleted |
| `.claude/INDEX.md` | Remove all references to deleted pointer files |
| `CLAUDE.md` | Update read-order section; remove references to deleted files |

---

## Acceptance Criteria

- `ls .claude/ARCHITECTURE.md .claude/ROADMAP.md .claude/MODEL_POLICY.md .claude/MEMORY.md .claude/QUALITY_TRACKING.md` returns "No such file or directory" for all 5
- `ls MEMORY.md QUALITY_TRACKING.md` returns "No such file or directory" for both
- `grep -E "\.claude/(ARCHITECTURE|ROADMAP|MODEL_POLICY|MEMORY|QUALITY_TRACKING)\.md" CLAUDE.md` returns zero results
- `grep -E "\.claude/(ARCHITECTURE|ROADMAP|MODEL_POLICY|MEMORY|QUALITY_TRACKING)\.md" .claude/INDEX.md` returns zero results
- All existing tests pass
