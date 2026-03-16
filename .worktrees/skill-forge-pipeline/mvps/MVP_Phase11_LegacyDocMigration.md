# MVP Phase 11 — Legacy Doc Migration

**Goal:** Translate `.claude-development/` from an active development pipeline to a clearly-marked legacy documentation archive. Move its key content into the canonical locations (`mvps/`, `roadmaps/`, `.claude/knowledge/`), and mark the directory as read-only historical reference. After this phase, `.claude-development/` contains only historical audit logs and design records — no active development artifacts.

**Source finding:** NEW_MVPS.md — "old development pipeline in .claude-development should be translated to mvps and roadmaps as legacy documentation"

---

## Definition of Done

- [X] `.claude-development/README.md` updated to clearly state this is a legacy archive (read-only after Clockwork v18)
- [X] `Clockwork_MVP_Chain.md` summarized/indexed in `mvps/archive/MVP_Chain_Legacy.md` with a pointer back to `.claude-development/`
- [X] `.claude-development/designs/` ADRs and spec docs indexed in `.claude/knowledge/index.md` under "Legacy Designs"
- [X] `.claude-development/milestones/index.md` content merged into `roadmaps/` archive
- [X] `MVP_RULE.md` in `.claude-development/` reconciled with `.claude/governance/mvp_development_standard.md` — one canonical version
- [X] `CLAUDE.md` updated: `.claude-development/` section notes it is legacy archive only
- [X] All existing tests pass (no source code changes)

---

## P11.1 — Mark `.claude-development/` as Legacy Archive

**Finding:** `.claude-development/README.md` presents the directory as an active development pipeline. This misleads contributors into treating it as a live working directory. As of Clockwork v18, all active MVP tracking is in `mvps/`, roadmaps in `roadmaps/`, and design decisions in `.claude/knowledge/`.

**Change:** Update `.claude-development/README.md` with the following additions at the top of the file:

```markdown
# ClaudeClockwork Legacy Development Archive

> **ARCHIVED — Read-only as of Clockwork v18.**
> This directory contains historical development artifacts for Clockwork up to and including v17.x.
> Do not add new content here.
>
> Active locations:
> - MVP plans → `mvps/`
> - Roadmaps → `roadmaps/`
> - Design decisions → `.claude/knowledge/`
> - Governance standards → `.claude/governance/`
```

Preserve all existing content below this header — do not delete historical records.

**Validation:**
```bash
grep -i "legacy\|read-only" .claude-development/README.md && echo PASS || echo FAIL
```

---

## P11.2 — Create `mvps/archive/MVP_Chain_Legacy.md`

**Finding:** `.claude-development/Clockwork_MVP_Chain.md` documents the full B-001 through B-030+ chain of foundational Clockwork build steps. This is historically significant but not an active planning document. Creating a summary index in `mvps/archive/` makes it discoverable from the canonical MVP location without duplicating content.

**Steps:**
1. Read `.claude-development/Clockwork_MVP_Chain.md`
2. Create `mvps/archive/` directory if it does not exist
3. Create `mvps/archive/MVP_Chain_Legacy.md` with:
   - Header: `# Clockwork MVP Chain — Legacy Index (v17 and earlier)`
   - Summary table listing each chain item (B-NNN, title, status)
   - Note: `Full chain: see .claude-development/Clockwork_MVP_Chain.md`
   - Cross-reference table linking chain items to the Phase 0–9 MVPs that implemented them

**Example table structure:**
| Chain ID | Title | Status | Implemented By |
|----------|-------|--------|----------------|
| B-001 | Foundation cleanup | Complete | MVP_Phase0_FoundationCleanup.md |
| B-002 | Manifest hardening | Complete | MVP_Phase1_ManifestHardening.md |
| ... | ... | ... | ... |

**Acceptance:** `mvps/archive/MVP_Chain_Legacy.md` exists and contains the pointer to `.claude-development/Clockwork_MVP_Chain.md`.

---

## P11.3 — Index `.claude-development/designs/` in `.claude/knowledge/index.md`

**Finding:** `.claude-development/designs/` contains architecture decision records (ADRs) and spec documents that informed the current Clockwork implementation. They are not indexed anywhere in `.claude/knowledge/`, making them invisible to the knowledge management system.

**Change:** Add a "Legacy Design Records" section to `.claude/knowledge/index.md` with the following entries:

| File | Description | Status |
|------|-------------|--------|
| `.claude-development/designs/adr_capability_enforcement.md` | ADR: capability enforcement model for agent permissions | Superseded by `.claude/contracts/schemas/` |
| `.claude-development/designs/adr_runtime_critics_integration.md` | ADR: runtime integration of Technical and Systemic critics | Active (critics still in use) |
| `.claude-development/designs/B-010_runtime_critics_design.md` | Design: runtime critics pipeline (B-010 chain item) | Legacy |
| `.claude-development/designs/B-013_adaptive_router_v1_design.md` | Design: adaptive model router v1 (B-013 chain item) | Superseded by bandit router |
| `.claude-development/designs/capabilities_spec.yaml` | Spec: capability names and permission scopes | Legacy — see `.claude/contracts/schemas/` |
| `.claude-development/designs/command_allowlist_spec.yaml` | Spec: allowed shell commands per agent role | Legacy |
| `.claude-development/designs/critic_gates_spec.yaml` | Spec: critic gate thresholds and escalation rules | Legacy — see `.claude/governance/` |
| `.claude-development/designs/eval_shadow_ab_cbl_spec.md` | Spec: shadow A/B evaluation and CBL eval design | Active reference for `.claude/eval/` |
| `.claude-development/designs/per_agent_capability_matrix.md` | Matrix: per-agent capability assignments | Legacy — see `.claude/agents/` |

**Steps:**
1. Read `.claude/knowledge/index.md`
2. Append the "Legacy Design Records" section (do not overwrite existing content)
3. Verify the section contains at least 5 entries

**Validation:**
```bash
grep -c "Legacy Design Records\|\.claude-development/designs" .claude/knowledge/index.md
# Must return >= 2
```

---

## P11.4 — Reconcile `MVP_RULE.md` with `mvp_development_standard.md`

**Finding:** `.claude-development/MVP_RULE.md` and `.claude/governance/mvp_development_standard.md` define overlapping rules for MVP structure. Having two sources of truth for MVP authoring rules creates drift. `.claude/governance/mvp_development_standard.md` is the canonical location per the governance hierarchy.

**Steps:**
1. Read both files
2. Identify any rules in `.claude-development/MVP_RULE.md` not covered by `mvp_development_standard.md`
3. If gaps exist, add them to `.claude/governance/mvp_development_standard.md` with a note: `# Merged from .claude-development/MVP_RULE.md (Phase 11)`
4. Overwrite `.claude-development/MVP_RULE.md` with a pointer document:

```markdown
# MVP_RULE.md — Pointer

This file has been superseded as of Clockwork v18.

The canonical MVP development standard is:
  .claude/governance/mvp_development_standard.md

This file is retained as a historical reference only. Do not edit.
```

**Acceptance:** `.claude-development/MVP_RULE.md` contains the word "superseded" and a path to the canonical file. `.claude/governance/mvp_development_standard.md` is the single authoritative source.

---

## P11.5 — Update `CLAUDE.md`

**Finding:** `CLAUDE.md` does not mention `.claude-development/` in the Directory Structure section. Omitting it means contributors discovering the directory have no context for its purpose or status.

**Change:** Add to the Directory Structure section of `CLAUDE.md`:

```
.claude-development/    # Legacy development archive (Clockwork v17 and earlier). Read-only.
                        # Active MVPs → mvps/. Active roadmaps → roadmaps/.
                        # Design records indexed in .claude/knowledge/index.md.
```

---

## Files Changed

| File | Change |
|------|--------|
| `.claude-development/README.md` | Add legacy archive header and read-only guidance |
| `.claude-development/MVP_RULE.md` | Convert to pointer to `.claude/governance/mvp_development_standard.md` |
| `mvps/archive/MVP_Chain_Legacy.md` | New — summary index of the B-NNN legacy MVP chain |
| `.claude/knowledge/index.md` | Add "Legacy Design Records" section with 9 entries |
| `.claude/governance/mvp_development_standard.md` | Absorb any MVP_RULE.md rules not already present |
| `CLAUDE.md` | Add `.claude-development/` entry to Directory Structure |

---

## Acceptance Criteria

- `.claude-development/README.md` contains the word "legacy" and "read-only"
- `mvps/archive/MVP_Chain_Legacy.md` exists and references `.claude-development/Clockwork_MVP_Chain.md`
- `.claude/knowledge/index.md` lists at least 5 legacy design records under a "Legacy Design Records" heading
- `.claude-development/MVP_RULE.md` contains "superseded" and points to `.claude/governance/mvp_development_standard.md`
- All existing tests pass (no source code changes in this phase)

---

## Implementation Notes

- All changes in this phase are documentation-only. No Python source files are modified.
- Read `.claude-development/Clockwork_MVP_Chain.md` before writing P11.2 — the chain numbering (B-NNN) must be accurate in the legacy index.
- Read `.claude/knowledge/index.md` before editing it in P11.3 — append only, do not overwrite existing sections.
- P11.4 requires reading both rule files before writing; do not assume `mvp_development_standard.md` is a superset without checking.
- The `roadmaps/` merge mentioned in the Definition of Done (milestones/index.md content) should be treated as a light indexing task, not a full content migration — add a pointer entry in `roadmaps/` pointing back to `.claude-development/milestones/`.
