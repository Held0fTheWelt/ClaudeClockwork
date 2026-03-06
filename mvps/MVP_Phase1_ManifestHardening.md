# MVP Phase 1 — Manifest Hardening

**Goal:** Turn the manifest/registry system from a working prototype into a production-reliable contract. Every manifest must be verifiable without running the skill.

---

## Definition of Done

- [ ] All 34 manifests pass JSON schema validation
- [ ] All 34 manifest entrypoints resolve without `ModuleNotFoundError`
- [ ] `manifest_validate` checks schema + importability and returns detailed errors
- [ ] `skill_scaffold` produces manifests that pass `manifest_validate` on first run
- [ ] A new skill added via scaffold is immediately callable via the CLI
- [ ] All existing tests pass; 2 new tests added

---

## Deliverables

### D1.1 — Manifest JSON Schema

**File:** `.claude/contracts/schemas/manifest_schema.json`

Required fields:
```json
{
  "id": "string — matches directory name",
  "name": "string — human-readable",
  "description": "string — one sentence",
  "version": "string — semver",
  "category": "string — one of: meta | qa | cleanup | evidence | routing | docs | performance | planning | analysis | misc | demo",
  "entrypoint": "string — module:ClassName",
  "permissions": ["array of strings from configs/permissions.json"],
  "tags": ["optional array of strings"],
  "aliases": ["optional array of alternate skill IDs"]
}
```

Optional fields: `tags`, `aliases`, `legacy_bridge` (bool).

---

### D1.2 — Extend `manifest_validate` Skill

**File:** `.claude/skills/meta/manifest_validate/skill.py`

Extend to check (in order):
1. All required fields present
2. Fields match declared types
3. `category` is one of the allowed values
4. `permissions` entries all exist in `configs/permissions.json`
5. `entrypoint` resolves via `SkillLoader.load_skill_class()` — actually imports the class
6. Loaded class is a subclass of `SkillBase`

Return detailed error list per check, not just `valid: true/false`.

---

### D1.3 — Normalize All 34 Manifests

Audit each `manifest.json` against the schema from D1.1. For each:
- Add any missing required fields
- Correct any wrong `category` values
- Ensure `permissions` entries match `configs/permissions.json` keys
- Ensure `entrypoint` resolves (after D0.1 fix)

**Batch validation command:**
```bash
python3 -m claudeclockwork.cli --skill-id manifest_validate --inputs '{"path": ".claude/skills", "all": true}'
```

---

### D1.4 — `skill_scaffold` Manifest Template Update

**File:** `.claude/skills/meta/skill_scaffold/skill.py`

Update the scaffold template to emit manifests compliant with the D1.1 schema. Add a `--validate` flag that calls `manifest_validate` immediately after scaffolding.

---

### D1.5 — `SkillRegistry` Strict Mode

**File:** `claudeclockwork/core/registry/skill_registry.py`

Add `strict=False` parameter to `build_registry()`. When `strict=True`:
- Reject any manifest that fails schema validation at registry build time
- Log a warning (not error) for each invalid manifest in default mode
- Expose `registry.validation_errors` list for inspection

---

## Tests

```python
def test_all_manifest_entrypoints_resolve():
    """No manifest should have an unresolvable entrypoint."""
    registry = build_registry(Path(".").resolve())
    for item in registry.list_skills(enabled_only=False):
        manifest = registry.get_manifest(item.name)
        cls = registry._loader.load_skill_class(manifest.entrypoint)
        assert issubclass(cls, SkillBase)

def test_manifest_validate_catches_bad_entrypoint():
    """manifest_validate must return valid=false for a broken entrypoint."""
    result = run_manifest_skill({
        "request_id": "test",
        "skill_id": "manifest_validate",
        "inputs": {"entrypoint": "nonexistent.module:FakeClass"}
    }, Path(".").resolve())
    assert result["outputs"]["valid"] is False
    assert any("entrypoint" in e for e in result["outputs"]["errors"])
```

---

## Dependencies

- Phase 0 D0.1 (entrypoint namespace fix) must be complete
- Phase 0 D0.3 (governance translation) recommended before this phase — agents will read these during implementation

## Files changed

| File | Change |
|------|--------|
| `.claude/contracts/schemas/manifest_schema.json` | New — formal manifest schema |
| `.claude/skills/meta/manifest_validate/skill.py` | Extend with schema + import checks |
| `.claude/skills/meta/skill_scaffold/skill.py` | Update template + add validate flag |
| `claudeclockwork/core/registry/skill_registry.py` | Add strict mode + validation_errors |
| All 34 `manifest.json` files | Normalize fields |
| `tests/test_manifest_hardening.py` | New test file |
