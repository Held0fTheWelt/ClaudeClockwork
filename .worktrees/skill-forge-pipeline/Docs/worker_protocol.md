# Worker Protocol (Phase 35)

- Job envelope: job_id, idempotency_key, node_spec, input_artifact_refs (hashes), resource_hints, security_context, expected_output_schema.
- Local worker processes envelope using existing runtime; telemetry and artifacts under runtime root.
- Artifact shipping: content-addressed bundles with manifest and hashes; redact where required.
- Retry: retryable (timeouts, transient) vs non-retryable (policy_denied, validation). Idempotency: same key returns cached result.
