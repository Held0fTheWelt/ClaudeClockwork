# MVP Phase 0 — Foundation & Cleanup

**Goal:** Eliminate all blocking drift and language violations identified in the VERIFY 2026-03-06 audit before any new features are built.

---

## Definition of Done

- [X] All English-language policy checks pass (no German in active project-facing files)
- [X] `manifest_validate` can import each manifest's entrypoint without error
- [X] "Oodle Tier" naming replaced with "Local Model Tier" everywhere
- [X] Boot check passes on clean checkout
- [X] All 5 existing tests still pass

---

## Deliverables

### D0.1 — Manifest Entrypoint Namespace Fix (Blocking)

**Problem:** Manifests declare `skills.bundle.*` as entrypoint but `sys.path` adds `.claude/skills`, making `bundle.*` the correct prefix. The `LegacySkillAdapter` pattern currently bypasses importlib, masking the error.

**Fix options (pick one):**
- Option A: Update `loader.py` to strip the `skills.` prefix and resolve `bundle.*` directly from `.claude/skills`
- Option B: Update all 34 `manifest.json` files — change `"entrypoint": "skills.bundle.foo.skill:FooSkill"` → `"entrypoint": "bundle.foo.skill:FooSkill"`

**Validation:** `python3 -c "from claudeclockwork.core.registry.loader import SkillLoader; SkillLoader().load_skill_class('bundle.evidence_bundle_build.skill:EvidenceBundleBuildSkill')"` must succeed.

**Files:** `claudeclockwork/core/registry/loader.py` and/or all `manifest.json` files

---

### D0.2 — Language Migration: Agent Definition Files

**Files:** All 39 `.md` files in `.claude/agents/`
**Priority:** Critical — agents read these files every session; German degrades reasoning quality

Key files (translate first):
- `.claude/agents/specialists.md`
- `.claude/agents/team_lead.md`
- `.claude/agents/context_packer.md`
- `.claude/agents/critics/technical.md`
- `.claude/agents/critics/systemic.md`

**Rule:** Full translation. No mixed German/English in any single file.

---

### D0.3 — Language Migration: Governance Files

**Files:** All 15 `.md` files in `.claude/governance/`
**Priority:** Critical — governance rules define system behavior

Files to translate:
- `execution_protocol.md`, `workflow_triggers.md`, `escalation_matrix.md`, `git_workflow.md`
- `file_ownership.md`, `routing_matrix.md`, `decision_policy.md`, `rule_discovery.md`
- `self_improvement.md`, `task_archival.md`, `model_escalation_policy.md`, `review_process.md`
- `ollama_integration.md`, `document_placement.md`, `mvp_development_standard.md`

---

### D0.4 — Language Migration: Skill README Files

**Files:** All `README.md` files in `.claude/skills/` subdirectories (~106 files)
**Priority:** High — skill documentation must be readable by English-mode agents

Approach: batch translate, one skill directory at a time.

---

### D0.5 — Language Migration: PDF Quality Templates

**Files:** 8 files in `.claude/skills/pdf_quality/`
**Priority:** High — templates generate output documents

Files:
- `templates/lastenheft.template.md` → translate to English (requirements spec template)
- `templates/first_steps.template.md` → translate
- `templates/tutorial.template.md` → translate
- `templates/api_reference.template.md` → translate
- `rubric.md` → translate
- `README.md` → translate
- `examples/sample_lastenheft.md` → replace with English example
- `examples/sample_first_steps.md` → replace with English example

---

### D0.6 — Rename "Oodle Tier" to "Local Model Tier"

**Files to update:**
- `CLAUDE.md` — model routing table header
- `.claude/governance/` — any reference to "Oodle tier", "Oodle-first"
- `.claude/tools/skills/budget_router.py` — field `oodle_tier`
- `.claude/tools/skills/efficiency_review.py` — any Oodle references
- Any other skill `.py` files referencing "oodle_tier"

**Search command:** `grep -r "oodle\|Oodle" .claude/tools/skills/ .claude/governance/ CLAUDE.md --include="*.py" --include="*.md" -l`

---

### D0.7 — Fix Stale `llamacode` Imports

**Files:**
- `.claude/tools/skills/bandit_router_select.py` — remove `from llamacode.core.bandit_router import BanditRouter`
- `.claude/tools/skills/escalation_router.py` — remove equivalent stale import

**Action:** Delete the commented-out `llamacode` import lines. Both files already have `# type: ignore` fallbacks.

---

### D0.8 — Fix Stale INDEX.md Paths

**File:** `.claude/INDEX.md`

**Stale references to fix:**
- `.llama_runtime/knowledge/writes/` → update to reflect `.llama_runtime/` layout
- `skills/registry.md` path implication → correct to `registry/skill_index.json`

---

### D0.9 — Populate `.project/MEMORY.md`

**File:** `.project/MEMORY.md`

Add entries for:
- Architecture decision: `claudeclockwork/` is the canonical package (not `llamacode/` or `oodle/`)
- Stable finding: dual skill dispatch (legacy runner 97 skills, manifest CLI 34 skills)
- Stable finding: manifest entrypoint namespace fix required before Phase 1
- User preference: English-only project language

---

## Tests

No new tests needed for Phase 0. All existing 5 tests must continue to pass after each change.

Add one validation test for D0.1:
```python
def test_manifest_entrypoints_are_importable():
    """All manifest skills must resolve their entrypoint without ModuleNotFoundError."""
    from claudeclockwork.runtime import build_registry
    registry = build_registry(Path(".").resolve())
    for item in registry.list_skills(enabled_only=False):
        manifest = registry.get_manifest(item.name)
        # should not raise
        registry._loader.load_skill_class(manifest.entrypoint)
```

---

## Dependencies

None — Phase 0 is the prerequisite for all other phases.

## Estimated scope

- D0.1: 1 file (loader.py) or 34 manifest.json files — isolated, low risk
- D0.2–D0.5: documentation translation — no code changes, high volume
- D0.6–D0.8: targeted find-and-replace — low risk
- D0.9: write-only — no risk
