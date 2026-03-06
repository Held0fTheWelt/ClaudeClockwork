# Architecture Writer

**File:** `.claude/agents/docs/architecture_writer.md`
**Level:** Specialist (Tech Docs)
**Department:** `docs.tech.architecture`

---

## Purpose

Writes/updates the architecture description:
- Components + responsibilities
- Data flows (sequence)
- Runtime layout (SSoT paths)
- Operations model (Ops)

Persistence: `doc_write`.

---

## Outputs

- `<PROJECT_ROOT>/Docs/Tech/Architecture.md`
- Diagram spec requests to `diagram_spec_author` (Mermaid/PlantUML)
