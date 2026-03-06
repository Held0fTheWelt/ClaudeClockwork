# Source-of-Truth for Product Code: `claudeclockwork/`

> **Note:** This policy supersedes the original `src/` requirement as of Clockwork v18.
> The `src/` directory does not exist in this repository; `claudeclockwork/` is the canonical package.

## Rule (hard requirement)

All generated **application code** and **plugin/application files** that represent the product MUST originate under one of:

- `claudeclockwork/` — Python package; CLI, runtime, registry, executor, bridge, and core modules
- `.claude/skills/*/skill.py` — manifest skill implementations (one class per skill, extends `LegacySkillAdapter` or `SkillBase`)
- `.claude/tools/skills/*.py` — legacy skill modules (one `run(req)` function per file)

## Non-goals

- This rule does NOT apply to the Clockwork control plane itself (agent definitions, governance docs, JSON schemas under `.claude/`).
- Reports, evidence, generated docs, and performance telemetry belong under `.llama_runtime/` or `.claude-performance/`.
- Test code lives under `tests/`.

## Why

- Enables deterministic cleanup and refactors
- Reduces drift and "mystery code" in random folders
- Makes hardening/cleanup skills safe to apply

## Enforcement

- `hardening_scan_fix` scenario `enforce_src_origin_rule` flags product-code files found outside the three canonical locations above.
