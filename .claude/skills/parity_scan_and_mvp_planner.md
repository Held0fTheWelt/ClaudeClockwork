# Skill: parity_scan_and_mvp_planner

**Category:** Audit / Planning
**Status:** active
**Default model:** Sonnet (CCW policy: planning/audits run on Sonnet)
**Added:** 2026-03-02 (CCW-MVP08)

---

## Purpose

Scans the repo to build a capability parity matrix by comparing what the clockwork currently implements against the targets defined in the MVP chain and Power Audit reports. Identifies gaps (✗ GAP) and partial implementations (~ PARTIAL), produces a prioritized missing features backlog, and optionally generates a dependency-aware MVP pre-plan for the next milestone.

This skill is the canonical mechanism for the **per-MVP parity scan** trigger defined in `.claude-development/audits/audit_cadence.md`.

---

## Input (`skill_request_spec`)

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `run_date` | string (YYYY-MM-DD) | Yes | — | Date of the scan run; used in output file names |
| `scan_scope` | array of strings | No | full repo | List of directories to scan (e.g., `[".claude", "llamacode", "tests"]`) |
| `reference_mvp_chain` | string | No | `.claude-development/Clockwork_MVP_Chain.md` | Path to the MVP chain specification document |
| `output_dir` | string | No | `.claude-development/audits/parity/` | Directory where parity matrix and backlog are written |
| `generate_mvp_plan` | boolean | No | `true` | Whether to also generate an M* pre-plan |
| `mvp_plan_output_dir` | string | No | `.claude-development/milestones/` | Directory for the generated M* plan |

**Schema:** `.claude/contracts/schemas/parity_scan_and_mvp_planner.schema.json`
**Example:** `.claude/contracts/examples/parity_scan_and_mvp_planner_example.json`

---

## Output (`skill_result_spec`)

| Field | Type | Description |
|-------|------|-------------|
| `parity_matrix` | string | Absolute path to written parity matrix file |
| `backlog` | string | Absolute path to written missing features backlog |
| `mvp_plan` | string \| null | Absolute path to written M* pre-plan (null if `generate_mvp_plan: false`) |
| `gap_count` | integer | Total number of ✗ GAP items found |
| `partial_count` | integer | Total number of ~ PARTIAL items found |
| `full_count` | integer | Total number of ✓ FULL items found |
| `p0_count` | integer | Number of P0-priority backlog items |
| `p1_count` | integer | Number of P1-priority backlog items |
| `p2_count` | integer | Number of P2-priority backlog items |
| `status` | enum | `ok` \| `partial` \| `error` |
| `errors` | array | List of error messages if `status` is `error` or `partial` |

---

## Execution Steps

The skill follows these steps in order:

1. **Read MVP chain** — Load `reference_mvp_chain` to extract capability targets for each MVP (MVP01–latest)
2. **Read audit inputs** — Load Power Audit reports from `.report/` (inventory, QA findings, gap analysis)
3. **Scan repo** — For each capability target: check whether the referenced file exists; classify as ✓ FULL / ~ PARTIAL / ✗ GAP
4. **Build parity matrix** — Write `parity_matrix_<run_date>.md` to `output_dir` with evidence file citations
5. **Build backlog** — Extract all ✗ GAP and ~ PARTIAL items; prioritize P0/P1/P2 by security/leverage/effort
6. **Write backlog** — Write `missing_features_backlog_<run_date>.md` to `output_dir`
7. **Generate M* plan** (if `generate_mvp_plan: true`) — Build dependency-aware plan for top P0+P1 items; write to `mvp_plan_output_dir`
8. **Return result spec** — Emit `skill_result_spec` with counts, paths, and status

---

## Checklist (run before publishing output)

- [ ] Every capability row in the parity matrix cites a real file path as evidence (not a placeholder)
- [ ] Every ✗ GAP row has a corresponding backlog entry (B-NNN)
- [ ] Backlog is sorted strictly by priority: P0 → P1 → P2 (no P1 item before all P0 items)
- [ ] Every backlog item has: ID, Feature, Gap Evidence (citing `.report/` file + defect/gap number), Effort, Unlocks
- [ ] MVP pre-plan is dependency-aware: no step depends on an unfinished preceding step
- [ ] Model policy followed: planning/design uses Sonnet, not Haiku or Opus (unless deep review requested)
- [ ] All outputs are written under `.claude-development/` (not `.claude/`)
- [ ] `run_date` in output file names matches the `run_date` input field
- [ ] Parity matrix summary table counts match the individual row counts

---

## Templates

- **Schema:** `.claude/contracts/schemas/parity_scan_and_mvp_planner.schema.json`
- **Example:** `.claude/contracts/examples/parity_scan_and_mvp_planner_example.json`
- **Audit cadence:** `.claude-development/audits/audit_cadence.md`
- **MVP chain:** `.claude-development/Clockwork_MVP_Chain.md`

---

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `qa_gate` | Complementary — gate runs checks; this skill audits capability coverage |
| `evidence_bundle_build` | Downstream — evidence bundles may be built from parity scan outputs |
| `doc_write` | Downstream — parity matrix and backlog are documentation artifacts |
| `skill_gap_detect` | Related — detects unimplemented skills; feeds into this skill's row #17 |

---

## Notes

- **Design-first:** This skill produces design/planning artifacts only. It does not modify the repo or implement missing features.
- **Cadence:** Run automatically after each MVP chain execution (see `.claude-development/audits/audit_cadence.md`).
- **No Python implementation required** — this skill is executed by Claude Code (Sonnet) reading and writing Markdown; no `.py` file needed in `.claude/tools/skills/`.
