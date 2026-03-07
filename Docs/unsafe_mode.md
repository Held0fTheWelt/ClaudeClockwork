# Unsafe Mode (Phase 34)

- Unsafe mode is a **local-only** override. It must be set explicitly (e.g. env or flag).
- **CI:** Unsafe mode is forbidden in CI. QA/release gates fail if unsafe mode is enabled.
- When enabled locally, the fact is logged (no secret material). Use only for debugging.
