# Deprecations Registry

> All planned removals or breaking changes must be listed here before removal. Lifecycle: warn → block → remove.

## Format

Each entry:

- **Symbol/feature:** name (CLI command, flag, or public API symbol)
- **Deprecated in:** version (e.g. 0.2.0)
- **Will remove in:** MAJOR version or "TBD"
- **Replacement:** what to use instead
- **Status:** `warn` | `block` | `removed`

---

## Current entries

*(None as of contract version 1.0.)*

---

## Adding an entry

1. Add a row to the table above with status `warn`.
2. Ensure replacement is documented and available in the same or next MINOR release.
3. In a later release, move to `block` (optional: feature flag to re-enable).
4. In the next MAJOR release, move to `removed` and delete the symbol.
