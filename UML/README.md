# Code-aligned UML (Clockwork)

Implementation-facing diagrams for component SADs. Each package under
`Components/<slug>/` has `README.md`, `TRACEABILITY.md`, and diagram folders
with `.md` (Mermaid preview) + `.puml` source companions.

## Required folders (component minimum)

- `components/` - C4 context, container, component
- `sequence/` - primary and degraded paths
- `states/` - lifecycle diagrams

## Templates

Copy from [`_templates/c4/`](_templates/c4/) when adding a component package.

## Generated bundles

`UML/generated/` holds tool output (gitignored). Curated packages under
`Components/` are hand-maintained from those bundles and validated by
`tests/gates/test_architecture_documentation_gate.py`.
