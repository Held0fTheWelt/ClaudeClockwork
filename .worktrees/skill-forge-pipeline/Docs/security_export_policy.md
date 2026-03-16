# Security Export Policy (Phase 23)

- **Exports must be redacted** unless explicitly running in "unsafe local mode" (e.g. developer machine, not CI).
- **CI must never produce unredacted bundles.** The release/QA gate treats unredacted export as a failure when in CI context.
- Redaction rules: see `claudeclockwork.core.redaction` (tokens, API keys, paths, PII-like patterns).
- Evidence bundle spec: `Docs/evidence_bundle_spec.md`.
