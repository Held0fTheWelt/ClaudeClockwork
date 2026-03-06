# MVP Phase 4 — Plugin Runtime

**Goal:** Wire the existing plugin JSON scaffolds into a live Python plugin loader. Skills can declare plugin dependencies; the executor validates them at runtime.

---

## Definition of Done

- [ ] `plugins/*/plugin.json` files are discovered and loaded at executor build time
- [ ] A skill declaring a plugin dependency fails cleanly if that plugin is disabled
- [ ] `plugin_registry_export` reports real enable/disable state from disk
- [ ] Enable/disable state persists across sessions (written to `registry/plugin_index.json`)
- [ ] Lifecycle hooks (`healthcheck`) are callable from the CLI
- [ ] Boot check passes with plugin system loaded
- [ ] All existing tests pass; 4 new tests added

---

## Current State

```
plugins/
  filesystem/
    plugin.json    ← defines 2 capabilities, fs:read/fs:write permissions
    README.md      ← "skeleton"
  git/
    plugin.json    ← defines 2 capabilities, git:read permission
    README.md      ← "skeleton"

registry/
  plugin_index.json    ← lists 2 plugins with metadata (not loaded by Python)
  installed_skills.json ← lists 34 skills (not loaded by Python)
```

Zero Python code currently loads these files.

---

## Deliverables

### D4.1 — Plugin Manifest Schema

**File:** `.claude/contracts/schemas/plugin_schema.json`

```json
{
  "id": "string",
  "name": "string",
  "version": "string (semver)",
  "description": "string",
  "capabilities": [
    {
      "id": "string",
      "description": "string",
      "permissions": ["array of permission strings"]
    }
  ],
  "lifecycle": {
    "healthcheck": "optional — module:function path",
    "on_install": "optional — module:function path",
    "on_enable": "optional — module:function path",
    "on_disable": "optional — module:function path"
  }
}
```

---

### D4.2 — Plugin Loader

**File:** `claudeclockwork/core/plugin/loader.py`

```python
class PluginLoader:
    def discover(self, plugin_root: Path) -> list[PluginManifest]:
        """Scan plugin_root/*/plugin.json and return parsed manifests."""

    def load_manifest(self, path: Path) -> PluginManifest:
        """Parse and validate a single plugin.json against plugin_schema.json."""
```

---

### D4.3 — Plugin Registry

**File:** `claudeclockwork/core/plugin/registry.py`

```python
class PluginRegistry:
    def list_plugins(self, enabled_only: bool = True) -> list[PluginManifest]: ...
    def is_enabled(self, plugin_id: str) -> bool: ...
    def enable(self, plugin_id: str) -> None: ...
    def disable(self, plugin_id: str) -> None: ...
    def get_capabilities(self, plugin_id: str) -> list[Capability]: ...
```

State stored in `registry/plugin_index.json`. State updates are atomic (write to temp, rename).

---

### D4.4 — Dependency Resolver

**File:** `claudeclockwork/core/plugin/dependency.py`

```python
class PluginDependencyResolver:
    def validate_skill(self, manifest: SkillManifest, plugin_registry: PluginRegistry) -> list[str]:
        """
        Return list of dependency error strings.
        Empty list = all dependencies satisfied.
        """
```

Skill manifests gain an optional `"requires_plugins": ["plugin_id"]` field in Phase 4.

---

### D4.5 — `runtime.py` Integration

**File:** `claudeclockwork/runtime.py`

Update `build_executor()` to:
1. Load `PluginLoader().discover(project_root / "plugins")`
2. Build `PluginRegistry` from discovered manifests + state in `registry/plugin_index.json`
3. Pass `PluginDependencyResolver(plugin_registry)` to `SkillExecutor`

Update `SkillExecutor.execute()` to call `dependency_resolver.validate_skill(manifest, plugin_registry)` before running — fail with descriptive error if dependencies not met.

---

### D4.6 — Update Native Skills: `plugin_registry_export`

**File:** `.claude/skills/plugins/plugin_registry_export/skill.py`

Update to call `PluginRegistry.list_plugins(enabled_only=False)` and return live state, not static JSON.

---

### D4.7 — Healthcheck Hook

Add to CLI:
```bash
python3 -m claudeclockwork.cli --plugin-healthcheck filesystem
```

Calls `plugin.lifecycle.healthcheck` function if declared, returns pass/fail.

---

## Tests

```python
def test_plugin_discovery_finds_both_plugins():
    from claudeclockwork.core.plugin.loader import PluginLoader
    plugins = PluginLoader().discover(Path("plugins"))
    ids = {p.id for p in plugins}
    assert "filesystem" in ids
    assert "git" in ids

def test_plugin_registry_enable_disable_persists():
    registry = build_plugin_registry(Path(".").resolve())
    registry.enable("filesystem")
    assert registry.is_enabled("filesystem")
    registry.disable("filesystem")
    assert not registry.is_enabled("filesystem")

def test_skill_fails_when_required_plugin_disabled():
    # A skill that requires the filesystem plugin, with filesystem disabled
    registry = build_plugin_registry(Path(".").resolve())
    registry.disable("filesystem")
    # Attempt to run a skill that requires filesystem
    result = run_manifest_skill({
        "skill_id": "some_fs_skill",
        "inputs": {}
    }, Path(".").resolve())
    assert result["status"] == "fail"
    assert "filesystem" in result["errors"][0]

def test_plugin_registry_export_reflects_live_state():
    result = run_manifest_skill({"skill_id": "plugin_registry_export", "inputs": {}}, ROOT)
    assert result["status"] == "ok"
    assert "plugins" in result["outputs"]
    assert len(result["outputs"]["plugins"]) == 2
```

---

## Dependencies

- Phase 3 complete — native skills provide stable `claudeclockwork.core.*` interface
- `configs/permissions.json` should have all permissions referenced in `plugin.json` files

## Files Changed / Created

| File | Change |
|------|--------|
| `claudeclockwork/core/plugin/__init__.py` | New package |
| `claudeclockwork/core/plugin/loader.py` | New — plugin discovery |
| `claudeclockwork/core/plugin/registry.py` | New — enable/disable state |
| `claudeclockwork/core/plugin/dependency.py` | New — dependency validation |
| `claudeclockwork/runtime.py` | Update `build_executor()` |
| `claudeclockwork/core/executor/executor.py` | Add dependency check |
| `.claude/contracts/schemas/plugin_schema.json` | New — formal plugin schema |
| `.claude/skills/plugins/plugin_registry_export/skill.py` | Update to use live registry |
| `tests/test_plugin_runtime.py` | New test file |

## Notes

- Do not add `requires_plugins` to any existing skill manifest in this phase — that would break existing tests. The dependency resolver validates only if the field is present.
- Plugin enable/disable state defaults to `enabled: true` for all discovered plugins until explicitly disabled.
