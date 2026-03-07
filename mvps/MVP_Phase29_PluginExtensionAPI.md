# MVP Phase 29 — Plugin Marketplace / Extension API

**Goal:** Enable safe, versioned extensions (skills, agents, critics, tools) without modifying core. Provide a clear plugin contract and loader with compatibility checks.

**Why now:** After governance (Phase 24) and distribution (Phase 28), plugins allow growth without repo chaos.

---

## Definition of Done

- [ ] Plugin manifest contract exists (schema + docs)
- [ ] Plugin discovery and loader exist (repo-local plugin directory)
- [ ] Compatibility checks exist (Clockwork version range)
- [ ] Plugin validation exists (capabilities, schemas, allowlists)
- [ ] Example plugin included (hello plugin with a simple skill/critic)
- [ ] Tests cover: load, reject incompatible, reject unsafe
- [ ] All existing tests pass

---

## X29.1 — Plugin Manifest Contract

**Files:**
- `.claude/contracts/schemas/plugin_manifest.schema.json` (new)
- `Docs/plugins.md` (new)

**Change:**
- Manifest fields:
  - plugin id/name
  - version + compatibility range
  - provided capabilities (skills/agents/critics)
  - optional dependencies
  - declared file access and external runner needs

**Acceptance:**
- Manifest validates example plugins.

---

## X29.2 — Plugin Loader + Discovery

**Files:**
- `claudeclockwork/plugins/loader.py`
- `claudeclockwork/plugins/registry.py`
- `tests/test_plugin_loader.py`

**Change:**
- Discover plugins under `plugins/` or `.clockwork_plugins/` (choose one).
- Load manifests, validate, register provided components.

**Acceptance:**
- Loader is deterministic (stable ordering).

---

## X29.3 — Safety & Governance Integration

**Files:**
- Capability policy integration (Phase 24)
- `Docs/plugin_security_policy.md` (new)

**Change:**
- Enforce:
  - capability allowlist
  - schema validation
  - external runner restrictions
  - resource limits

**Acceptance:**
- Unsafe plugin is rejected with a typed error.

---

## X29.4 — Example Plugin + Template

**Files:**
- `plugins/example_hello/` (new)
- `Docs/plugin_template.md` (new)

**Change:**
- Include minimal example and a copyable template.

**Acceptance:**
- Example plugin loads and runs a trivial component.

---
