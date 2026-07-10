# ClaudeClockwork ADRs

Architecture Decision Records for the rebooted Clockwork. Single ID stream
`ADR-CW-NNNN` with a domain column in the catalog; domain-split numbering is
deferred until the catalog needs it.

## Rules

- File name: `adr-cw-NNNN-<slug>.md`, IDs never reused.
- Every ADR is registered in [ADR-CATALOG.md](ADR-CATALOG.md) in the same
  commit that adds or changes it (same-change anchoring).
- Every ADR contains at least one fenced `mermaid` diagram.
- Statuses: `proposed` -> `accepted` -> (`superseded-by-<ID>` | `retired`).
- When a SAD consolidates an ADR, the SAD frontmatter lists it under
  `owns-adrs` and the ADR status notes the owning SAD.
- ADRs cite evidence (files, tags, test names), not conversation memory.
  The pre-reboot state is always citable as tag `v17-archive`.

## Lookup order

1. [ADR-CATALOG.md](ADR-CATALOG.md) for a keyword/domain match.
2. The owning SAD under `docs/architecture/` before changing cross-cutting behavior.
3. The UML package linked from the SAD frontmatter (`uml-package`).
