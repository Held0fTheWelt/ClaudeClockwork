# Multi-Project Graph Contract (Phase 58)

Pipelines may span projects. Handoff is **bundles only**; no raw paths across project boundaries.

## Contract

- **Graph:** Work graph may reference nodes that run in different projects. Each node has an optional `project_id`; default is current project.
- **Handoff:** Data between projects is only via exported/imported bundles (content-addressed). No direct file paths across projects.
- **Failure:** On failure, incident bundle is project-scoped (failing node's project).
- **Policies:** Per-project effective policy applies to nodes running in that project.

## Orchestrator

The orchestrator runs cross-project graphs by dispatching node execution to the project's runtime and passing only bundle refs (hashes) across boundaries.
