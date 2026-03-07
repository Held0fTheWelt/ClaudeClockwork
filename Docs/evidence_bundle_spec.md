# Evidence Bundle Spec (Phase 23)

Evidence bundles are redacted, shareable exports of runtime artifacts for debugging and auditing.

## Contents

- **Telemetry:** JSONL events (redacted: tokens, API keys, PII)
- **Eval summaries:** Eval run results and baselines from `.clockwork_runtime/eval/`
- **Routing decisions:** Routing outcome summaries (paths and host data redacted)
- **Artifacts:** Selected artifacts or hashes/references only (no raw secrets)

## Required metadata

- `timestamp` (ISO)
- `version` (Clockwork version from `.claude/VERSION`)
- `schema_version` (bundle manifest schema version)
- Host fingerprint: redacted or omitted

## Layout

- Bundle root: `.clockwork_runtime/redacted_exports/`
- Each export: `bundle_<timestamp>.zip` + `bundle_manifest_<timestamp>.json`
- Manifest describes: file list, hashes, sizes, redaction applied.

## Reference

Runtime root layout: `.clockwork_runtime/README.md` (Phase 19).
