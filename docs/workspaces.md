# Workspaces (Phase 33)

Multiple projects under a single workspace: per-project runtime root, profiles, telemetry. Cross-project references via exported bundles only (no direct paths).

## Config

- Workspace config lists projects: repo root, runtime root, allowed exports/imports.
- Discovery is deterministic (config file under workspace root or env).

## Boundary

- Writes outside project root (except runtime root) are denied with `policy_denied`.
- Reading sibling repos only via imported bundles, not file paths.
