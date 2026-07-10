# Work Graph Spec (Phase 30)

Work Graph is a DAG of nodes; execution is deterministic and resumable with caching.

## Node types

- **skill_call** — Invoke a skill by id; inputs/outputs as artifact refs.
- **agent_run** — Run an agent (optional).
- **gate_check** — Run a gate (e.g. release_check, planning_drift); fail stops the graph.
- **export_bundle** — Run evidence export (Phase 23).

## Artifacts

- Nodes consume and produce artifacts. References are paths under the runtime root or content hashes.
- Edges define data flow: node A output → node B input.

## Spec schema

See `.claude/contracts/schemas/work_graph.schema.json`. A graph has `nodes` (id, type, inputs, config) and `edges` (from_node, to_node, artifact_key).
