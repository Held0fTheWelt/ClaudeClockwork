# Document Placement Correction (BP-006)

> Documents incorrectly placed by the owner or through earlier tasks are moved to the correct location by a team — with owner consultation.

---

## Purpose

- **Consistency:** All documents are in the locations defined by Governance and File Ownership.
- **Discoverability:** Wrong placement leads to wrong routing and lost information.
- **Owner Consultation:** Whether to always proceed this way in a specific case is clarified with the owner.

---

## When Does BP-006 Apply?

- An agent or review determines: A document is **not** in the place designated by `file_ownership.md` and `workflow_triggers.md` (document naming, storage locations).
- Examples: Reference content in `Docs/Plans/`, plan in `Docs/Documentation/`, technical doc in `Docs/References/` when it's feature documentation.

---

## Process (Placement Correction)

1. **Finding**
   - The detecting agent/review documents: which file, current location, justified target location (incl. reference to `file_ownership.md` / document naming).

2. **Report to Team Lead**
   - Team Lead is informed: "Document [path] is probably incorrectly placed; suggested target location: [target]."

3. **Owner Consultation**
   - **Owner** is the agent responsible for the **target location** (or source location) according to `file_ownership.md`, or the user (Product Owner) if the document came from the user.
   - Team Lead coordinates consultation:
     - Should the document be moved to the suggested location?
     - Should this approach always be used for comparable cases in the future? (If yes → possibly record rule in Governance or MEMORY.md.)

4. **Move**
   - After approval, the **owner** of the target location performs the move (content to new location, possibly remove old file or replace with reference).
   - Cross-references and `.claude/knowledge/index.md` are adjusted by the Librarian Agent.

5. **No Silent Moves**
   - No agent moves documents without reporting and without agreed approval. Otherwise duplications, lost references, and file ownership violations occur.

---

## Ownership for Moves

- **Moving** is only permitted for whoever is either owner of the source file or owner of the target location (see `file_ownership.md`).
- If the detecting agent is not an owner: Domain Handoff to Team Lead → Team Lead activates the responsible owner for the move.

---

## Documentation

- Record significant corrections (e.g., new standard approach "always this way") in `<PROJECT_ROOT>/MEMORY.md` or `.claude/knowledge/decisions.md`.
- No separate document per move needed; note in review or task list if necessary.
