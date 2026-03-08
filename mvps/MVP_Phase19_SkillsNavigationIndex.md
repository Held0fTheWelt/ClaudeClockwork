# MVP Phase 19 — Skills Navigation Index

**Goal:** Create a comprehensive, machine-readable and human-friendly index of all 109 native skills, enabling fast discovery and organization across categories.

**Why now:** With 109 skills hierarchically organized across 15+ categories, navigation is difficult. A unified index with multiple views (by category, by frequency, by role, by function) makes the skill system discoverable.

---

## Definition of Done

- [x] ✅ Generate `.claude/skills/_index.json` (all 109 skills with metadata)
- [x] ✅ Generate `.claude/skills/INDEX.md` (human-readable navigation)
- [x] ✅ Index includes: skill_id, category, description, entrypoint, frequency
- [x] ✅ Multiple views: by category, by frequency
- [x] ✅ Deterministic output (stable ordering)
- [x] ✅ Test suite: 10/10 passing (test_skills_index.py)
- [x] ✅ All existing tests pass
- [x] ✅ Generator script: `.claude/tools/skills/generate_skills_index.py`

---

## 19.1 — Index Generator Script

**Files:**
- `.claude/tools/skills/generate_skills_index.py` (new)

**Change:**
- Scan `.claude/skills/` recursively for all `manifest.json` files
- Extract skill metadata (id, category, description, entrypoint, smoke_inputs)
- Generate JSON index with stable ordering
- Generate markdown navigation document

**Acceptance:**
- Script runs without errors
- Produces deterministic output (same run = same file hash)

---

## 19.2 — JSON Index Format

**Files:**
- `.claude/skills/_index.json`

**Structure:**
```json
{
  "metadata": {
    "version": "17.7.208",
    "generated": "2026-03-08T...",
    "total_skills": 109,
    "categories": 15
  },
  "skills": [
    {
      "id": "qa_gate",
      "category": "qa",
      "description": "...",
      "entrypoint": "claudeclockwork.core.gates.qa_gate:QAGateSkill",
      "path": ".claude/skills/qa/qa_gate",
      "frequency": "core"
    },
    ...
  ],
  "categories": {
    "qa": 11,
    "planning": 16,
    ...
  }
}
```

**Acceptance:**
- Valid JSON
- All 109 skills present
- Stable ordering (alphabetical within category)

---

## 19.3 — Markdown Navigation

**Files:**
- `.claude/skills/INDEX.md`

**Content:**
- Table of contents by category
- Quick reference: Core vs Extended skills
- Search tips and navigation guide
- Links to skill manifests

**Acceptance:**
- Readable in any markdown viewer
- All 109 skills listed
- Links are valid

---

## 19.4 — Integration

**Files:**
- `.claude/skills/README.md` (update to link to INDEX.md)
- Tests: `tests/test_skills_index.py`

**Change:**
- Skills README now points to INDEX.md as primary navigation
- Test verifies index completeness and determinism

**Acceptance:**
- Skill count in index matches actual .py files: 109
- Index regeneration produces identical output
- All tests pass

---
