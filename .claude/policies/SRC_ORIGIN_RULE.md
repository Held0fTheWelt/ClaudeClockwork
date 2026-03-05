# Source-of-Truth for Product Code: `src/`

## Rule (hard requirement)
All generated **application code** and all relevant **plugin/application files** that represent the product MUST originate under:

- `src/`

This includes (examples):
- Python packages/modules, Node/TS projects, C++ sources, build scripts that are part of the product
- Unreal plugins/modules (`.uplugin`, `Source/`, `Config/`), editor extensions, runtime modules
- Any files that are part of the shipped application/plugin

## Non-goals
- This rule does NOT apply to the Clockwork control plane itself (everything under `.claude/`).
- Reports, evidence, generated docs, and performance telemetry belong under `.llama_runtime/knowledge/writes/` or `.claude-performance/`.

## Why
- enables deterministic cleanup and refactors
- reduces drift and "mystery code" in random folders
- makes hardening/cleanup skills safe to apply

## Enforcement
- `hardening_scan_fix` scenario `enforce_src_origin_rule` flags product-code files found outside `src/`.
