# Failure Taxonomy (Phase 32)

Standard error codes used across skills, runners, router, and workgraph.

| Code | Meaning |
|------|---------|
| dependency_missing | Required tool/dependency not installed |
| policy_denied | Capability or path denied by policy |
| timeout | Operation exceeded time limit |
| validation_failed | Input/output validation failed |
| regression_blocked | Regression gate blocked the change |
| unknown_capability | Capability not in registry |
| runner_unavailable | No runner for capability |

Errors are consistent and machine-parseable for summaries and incident bundles.
