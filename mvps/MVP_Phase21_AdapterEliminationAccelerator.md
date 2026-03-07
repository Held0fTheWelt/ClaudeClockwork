# MVP Phase 21 — Adapter Elimination Accelerator

**Goal:** Make adapter elimination feasible by adding deterministic automation: normalize manifest metadata for legacy bridging, generate native SkillBase wrappers safely, and provide batch conversion tooling.

**Context (repo scan 2026-03-07):**
- Many manifest skills are still bridged/adapted from legacy `run(req)` skills.
- Adapter elimination is hard to finish manually without tooling.

---

## Definition of Done

- [ ] All manifest skills explicitly include `metadata.legacy_bridge` (true/false; no missing fields)
- [ ] A deterministic migration tool exists: `scripts/adapter_migrate.py`
- [ ] The tool can convert a selected list of skills (e.g. 10) from adapter to native wrapper deterministically
- [ ] Converted skills do not subclass a legacy adapter base class
- [ ] Tests added for:
  - metadata normalization
  - conversion smoke run for a small batch
- [ ] All existing tests pass

---

## A21.1 — Metadata Normalization

**Files:**
- `.claude/skills/**/manifest.json`

**Change:**
- Ensure every manifest has: `metadata.legacy_bridge: true|false`
- Provide a one-shot normalizer script that is idempotent.

**Acceptance:**
```bash
python scripts/adapter_migrate.py normalize-metadata
python scripts/adapter_migrate.py check-metadata
# check exits 0
```

---

## A21.2 — Native Wrapper Generation (No Adapter Base Class)

**Files:**
- `scripts/adapter_migrate.py`
- Converted `skill.py` files for selected skills

**Change:**
Generate a native SkillBase wrapper that:
- imports the legacy implementation
- calls the legacy `run(req)` deterministically
- maps outputs/errors/metrics to the modern contract
- does not inherit from a legacy adapter base class

**Acceptance:**
- Converted skills pass smoke tests and return contract-compliant outputs.

---

## A21.3 — Batch Conversion Plan (Batch 0)

**Change:**
- Convert 10 skills as “Batch 0” to validate the migration pattern.
- Record outcomes and adjust the generator for edge cases.

**Acceptance:**
- Batch 0 conversion is repeatable and produces identical outputs across runs.

---
