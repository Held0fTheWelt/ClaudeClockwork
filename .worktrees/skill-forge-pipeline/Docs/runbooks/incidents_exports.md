# Runbook: Incidents and Export Bundles

Incident handling and evidence export.

## Handle an incident (export bundle)

1. **Trigger:** Pipeline or gate fails; incident export may be triggered automatically or via CLI.
2. **CLI:** Run incident export command if documented (e.g. `clockwork export-incident` or equivalent). See [evidence_bundle_spec.md](../evidence_bundle_spec.md).
3. **Output:** Bundle written to configured path (e.g. `.report/` or `.clockwork_runtime/incidents/`).
4. **Validation:** Bundle contains expected artifacts (logs, config snapshot, redacted evidence) per spec.

**Rollback:** Delete or archive the bundle only; do not modify source logs used for audit.

---

## Export bundle for audit

1. **Scope:** Define what to include (per [security_export_policy.md](../security_export_policy.md)).
2. **Run:** Use evidence export skill or CLI with scope and output path.
3. **Validation:** Output exists, is readable, and redaction applied where required.

**Rollback:** Remove exported bundle if created in wrong location; re-export with correct scope.
