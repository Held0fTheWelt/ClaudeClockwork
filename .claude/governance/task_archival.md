# Task Archival (BP-005)

> Implemented tasks disappear from the active list; results go to references, feature docs, and knowledge index.
> Applies to Claude Code and all agent spawns after completing a plan.

---

## Purpose

- **Overview:** Active task list stays small and current.
- **Discoverability:** Results are anchored in reference and feature documents as well as the knowledge index.
- **Network:** All agents can access the relevant information in the future.

---

## When Does BP-005 Apply?

- Plan status was set to `IMPLEMENTED` or `CLOSED`.
- The associated task description (if maintained as Task_* in `Docs/Tasks/` or `Docs/Plans/`) is considered complete.

---

## Process (Archival Phase)

1. **Mark as Done**
   - In the current task overview (e.g., `<PROJECT_ROOT>/Docs/TASKS.md`, task index in `.claude/knowledge/index.md`, or central task list), mark the task as done.
   - Plan document: Set status to `IMPLEMENTED` or `CLOSED` (see Execution Protocol Step 8).

2. **Trigger Archival Workflow**
   - Team Lead coordinates the archival.
   - Involved agents (without direct agent-to-agent imports):
     - **Librarian Agent:** Transfer results to appropriate reference documents (`Docs/References/`, naming scheme `Ref_<Topic>.md`), maintain cross-references, update `.claude/knowledge/index.md`.
     - **Documentation Agent:** Create/update feature or function descriptions in `Docs/Documentation/`, with clear links to code and references.

3. **Storage Locations**
   - **Reference Knowledge:** `Docs/References/Ref_<Topic>.md` — Architecture and system references.
   - **Feature/Tech Docs:** `Docs/Documentation/` — Description of implemented features and technical details.
   - **Knowledge Index:** `.claude/knowledge/index.md` — Enter new or changed files, maintain topic tags and complete file map.

4. **New Document Types**
   - If additional document classes are to be introduced (e.g., new folder, new prefix), this must be agreed with the **Product Owner** (User). Only create and document in governance (e.g., `workflow_triggers.md`, `file_ownership.md`) after approval.

---

## Integration in Execution Flow

- The **archive** phase in `execution_protocol.md` includes:
  - Entry in `.claude/knowledge/decisions.md` (already defined),
  - **plus** the archival described here (results → Ref + Documentation + Index).
- Optionally, an explicit trigger **Archive:** in `workflow_triggers.md` can be used to trigger a pure archival task (e.g., retroactively for older completed tasks).

---

## Responsibilities (File Ownership)

| Action | Owner |
|--------|--------|
| Update task list / plan status | Team Lead |
| Create/modify `Docs/References/` | Librarian Agent |
| Create/modify `Docs/Documentation/` | Documentation Agent |
| Update `.claude/knowledge/index.md` | Librarian Agent |
| Entry in `.claude/knowledge/decisions.md` | Team Lead |

Domain Handoff via Team Lead when an agent needs write rights in another domain (see `file_ownership.md`).
