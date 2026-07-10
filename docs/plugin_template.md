# Plugin Template (Phase 29)

Copy and adapt for a new plugin.

## Layout

```
plugins/my_plugin/
  plugin.json    # Manifest (id, name, version, clockwork_compat, capabilities)
  skill.py       # Optional: simple component
```

## plugin.json minimal

```json
{
  "id": "my_plugin",
  "name": "My Plugin",
  "version": "0.1.0",
  "description": "Description",
  "clockwork_compat": ">=17",
  "capabilities": ["skill"]
}
```

## Compatibility

Set `clockwork_compat` to a version range (e.g. `>=17,<19`). The loader skips plugins that don't match the current Clockwork version.

## Example

See `plugins/example_hello/`.
