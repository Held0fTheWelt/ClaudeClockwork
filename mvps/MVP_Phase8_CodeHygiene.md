# MVP Phase 8 — Code & Governance Hygiene

**Goal:** Remove all stale, misleading, or incorrect artifacts identified in VERIFY 2026-03-06 that are not covered by Phases 1–7. No new features. Each task is self-contained and independently verifiable.

**Source findings:** VERIFY 2026-03-06 — S1 (Oodle Tier naming), F2 (SRC_ORIGIN_RULE.md), S3 (INDEX.md stale paths), C5 (Docs/ dual roots), C1 residual (llamacode import stubs in Python files).

---

## Definition of Done

- [ ] `oodle_tier` / `Oodle` do not appear as variable names or doc labels in any Python skill file
- [ ] `llamacode` import stubs removed from `bandit_router_select.py` and `escalation_router.py`
- [ ] `SRC_ORIGIN_RULE.md` replaced with a policy that matches the actual `claudeclockwork/` package layout
- [ ] `INDEX.md` references only paths that exist
- [ ] Root `Docs/` audit files either moved to `.project/Docs/References/` or documented as deliberately separate
- [ ] All existing tests pass

---

## H8.1 — Rename `oodle_tier` in Legacy Skill Python Code

**Finding:** VERIFY S1 — "Oodle Tier" appears in `budget_router.py` and `outcome_event_generate.py` as Python variable names / string literals.

**Files:**
- `.claude/tools/skills/budget_router.py` — `oodle_tier` variable(s)
- `.claude/tools/skills/outcome_event_generate.py` — `oodle_tier` reference(s)

**Change:** Rename `oodle_tier` → `local_model_tier` in all code and inline comments within these two files. Validate with:
```bash
grep -r "oodle_tier\|Oodle Tier" .claude/tools/skills/ claudeclockwork/
# Must return zero results
```

**Acceptance:** Zero occurrences of `oodle_tier` or `Oodle Tier` in `.py` files across the repository.

---

## H8.2 — Remove Stale `llamacode` Import Stubs

**Finding:** VERIFY C1 residual — `bandit_router_select.py` and `escalation_router.py` contain commented `from llamacode.core...` import attempts (marked `# type: ignore`).

**Files:**
- `.claude/tools/skills/bandit_router_select.py`
- `.claude/tools/skills/escalation_router.py`

**Change:** Remove the `llamacode` import lines (including any surrounding `try/except` blocks that exist solely for those imports). Do not alter any other logic.

**Validation:**
```bash
grep -n "llamacode" .claude/tools/skills/bandit_router_select.py .claude/tools/skills/escalation_router.py
# Must return zero results
```

---

## H8.3 — Replace `SRC_ORIGIN_RULE.md` with Accurate Policy

**Finding:** VERIFY F2 — Policy file `.claude/policies/SRC_ORIGIN_RULE.md` requires all generated code under `src/`. `src/` does not exist; the actual package is `claudeclockwork/`.

**Change:** Overwrite `SRC_ORIGIN_RULE.md` with a corrected policy:
- Remove all references to `src/`
- Replace with: all generated application code lives under `claudeclockwork/` (Python package), `.claude/skills/*/skill.py` (skill implementations), or `.claude/tools/skills/*.py` (legacy skill modules)
- Add note: "This policy supersedes the original `src/` requirement as of Clockwork v18."

**Acceptance:** `SRC_ORIGIN_RULE.md` references `claudeclockwork/` as the canonical code location, not `src/`.

---

## H8.4 — Fix Stale Path References in `INDEX.md`

**Finding:** VERIFY S3 — `.claude/INDEX.md` references `skills/registry.md` under `.claude/skills/` which does not exist at that path.

**Steps:**
1. Read `.claude/INDEX.md`
2. Locate the `skills/registry.md` reference
3. Either update it to point to the actual registry file (`claudeclockwork/core/registry/`) or remove the stale entry
4. Verify all other listed paths actually exist

**Validation:**
```python
# Every path listed in INDEX.md must exist
import re
from pathlib import Path
root = Path(".")
text = (root / ".claude/INDEX.md").read_text()
# Extract paths and verify
```

**Acceptance:** Every file path listed in `.claude/INDEX.md` resolves to an existing file or directory.

---

## H8.5 — Resolve `Docs/` vs `.project/Docs/` Split

**Finding:** VERIFY C5 — Root `Docs/` contains skill audit documents (`skill_system_audit_and_roadmap.md`, `full_skill_system_readme.md`, `skill_system_legacy_migration_matrix.*`) not referenced from governance. `CLAUDE.md` and `SYSTEM.md` declare `.project/Docs/` as the SSoT.

**Options (choose one):**
- **Move** root `Docs/` files into `.project/Docs/References/` — makes `.project/Docs/` the single root
- **Document the split** — add a note to `CLAUDE.md` stating root `Docs/` holds legacy skill audit artifacts (read-only archive); `.project/Docs/` is the live SSoT

**Recommended:** Document the split (lower risk than moving files that may be externally referenced).

**Change:** Add a section to `CLAUDE.md` under "Directory Structure":
```
Docs/          # Legacy skill audit archive (read-only, pre-v18). Not part of active governance.
               # Active documentation lives in .project/Docs/.
```

**Acceptance:** `CLAUDE.md` clearly explains the purpose of both `Docs/` directories.

---

## Tests

No new test files required — these are all doc/code cleanup tasks. Validate via:

```bash
# H8.1
grep -r "oodle_tier" .claude/tools/skills/ claudeclockwork/ && echo FAIL || echo PASS

# H8.2
grep -n "llamacode" .claude/tools/skills/bandit_router_select.py .claude/tools/skills/escalation_router.py && echo FAIL || echo PASS

# H8.3
grep "src/" .claude/policies/SRC_ORIGIN_RULE.md && echo STALE || echo PASS

# H8.4
python3 -c "
from pathlib import Path
text = Path('.claude/INDEX.md').read_text()
print('INDEX.md read OK, length:', len(text))
"
```

All existing tests must continue to pass after these changes.

---

## Dependency

None — all tasks in this phase are independent of Phases 7 and 9. Can be run in parallel with Phase 7.
H8.2 (llamacode cleanup) should be done **before** wrapping `bandit_router_select` and `escalation_router` in Phase 7 — or done inline during Phase 7 wrapping.

## Files Changed

| File | Change |
|------|--------|
| `.claude/tools/skills/budget_router.py` | Rename `oodle_tier` → `local_model_tier` |
| `.claude/tools/skills/outcome_event_generate.py` | Rename `oodle_tier` → `local_model_tier` |
| `.claude/tools/skills/bandit_router_select.py` | Remove `llamacode` import stub |
| `.claude/tools/skills/escalation_router.py` | Remove `llamacode` import stub |
| `.claude/policies/SRC_ORIGIN_RULE.md` | Replace with `claudeclockwork/`-accurate policy |
| `.claude/INDEX.md` | Fix stale `skills/registry.md` path reference |
| `CLAUDE.md` | Document `Docs/` vs `.project/Docs/` split |
