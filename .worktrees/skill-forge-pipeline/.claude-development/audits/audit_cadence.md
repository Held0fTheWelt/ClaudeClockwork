# Audit Cadence Specification

**Version:** 1.0
**Date:** 2026-03-02
**Status:** Active (replaces placeholder created in MVP07)
**Owner:** Team Lead

---

## Cadence Table

| Trigger | Type | Scope | Output | Owner |
|---------|------|-------|--------|-------|
| Per MVP completed | Parity scan | MVP deliverables vs targets in MVP chain | `parity_matrix_<date>.md` + `missing_features_backlog_<date>.md` | `parity_scan_and_mvp_planner` skill |
| Per milestone (M*) | Milestone audit | Full M* deliverables progress + gap resolution | `audit_log_<date>.md` entry (milestone section) | Team Lead |
| Weekly | Power test | Full capability check against parity matrix | `.report/weekly_power_report.md` | Eval harness (automated) |
| Pre-release | Full audit | Entire repo: inventory, QA findings, gap analysis, parity | `.report/` (full set) + parity matrix + backlog refresh | Opus Power Audit (manual) |

---

## Trigger Rules

### Parity Scan (per MVP)
- **When:** Automatic; triggered at conclusion of each MVP chain execution
- **Who triggers:** Team Lead or the executing agent after MVP deliverables are written
- **Scope:** Check all MVP deliverables exist; compare against MVP chain spec targets; generate matrix + backlog
- **Model:** Sonnet (default CCW policy)
- **Blocking:** Yes — next MVP in the chain should not begin until parity scan is complete and artifacts written
- **Skill:** `parity_scan_and_mvp_planner`

### Milestone Audit (per M* milestone)
- **When:** Manual; triggered by Team Lead when M* is declared done
- **Who triggers:** Team Lead
- **Scope:** Review all M* step outputs; verify success criteria met; update milestone index; create audit log entry
- **Model:** Sonnet for summary; Opus for deep defect review if issues found
- **Blocking:** Soft — M+1 milestone planning should wait for M* audit to be filed

### Weekly Power Test
- **When:** Scheduled (nightly/weekly CI run); can also be triggered manually
- **Who triggers:** Eval harness (automated) or Team Lead
- **Scope:** Run full capability check against the latest parity matrix; flag new regressions or improvements
- **Model:** Haiku for scanning; Sonnet for report generation
- **Output location:** `.report/weekly_power_report_<YYYY-MM-DD>.md`
- **Blocking:** No — informational; issues should be triaged and added to backlog

### Full Audit (pre-release)
- **When:** Manual; before any version bump or major release
- **Who triggers:** Team Lead with explicit user opt-in
- **Scope:** Full repo inventory, QA findings, gap analysis, parity matrix refresh, backlog update
- **Model:** Opus 4.6 (Power Audit)
- **Blocking:** Yes — version bump blocked until full audit passes clean or all P0 items resolved

---

## Output Naming Convention

| Artifact | Pattern | Example |
|----------|---------|---------|
| Parity matrix | `parity_matrix_<YYYY-MM-DD>.md` | `parity_matrix_2026-03-02.md` |
| Missing features backlog | `missing_features_backlog_<YYYY-MM-DD>.md` | `missing_features_backlog_2026-03-02.md` |
| Milestone plan | `M<N>_<name>_<YYYY-MM-DD>.md` | `M1_parity_followup_plan_2026-03-02.md` |
| Audit log entry | `audit_log_<YYYY-MM-DD>.md` | `audit_log_2026-03-02.md` |
| Weekly power report | `weekly_power_report_<YYYY-MM-DD>.md` | `weekly_power_report_2026-03-09.md` |
| Full audit reports | `.report/<NN>_<topic>_<YYYY-MM-DD>.md` | `.report/01_clockwork_inventory_entrypoints.md` |

All names use `YYYY-MM-DD` date format. No spaces; underscores as separators.

---

## Output Locations

| Artifact Type | Location |
|--------------|----------|
| Parity matrices | `.claude-development/audits/parity/` |
| Missing features backlogs | `.claude-development/audits/parity/` |
| Milestone plans | `.claude-development/milestones/` |
| Audit log entries | `.claude-development/audits/logs/` |
| Weekly power reports | `.report/` |
| Full audit report sets | `.report/` |

**Hard rule:** No audit outputs go into `.claude/`. Clockwork is read-only; `.claude-development/` is the write target for all audit/development artifacts.

---

## Archival Policy

| Artifact | Retention | Notes |
|----------|-----------|-------|
| Parity matrices | Keep last 10 | Older matrices → `audits/parity/archive/` |
| Missing features backlogs | Keep last 10 | Parallel to parity matrices |
| Milestone plans | Permanent | All M* plans kept; never deleted |
| Audit log entries | Keep last 30 | Rolling 30-entry window per log file |
| Weekly power reports | Keep last 8 (2 months) | Older → `.report/archive/` |
| Full audit report sets | Permanent | Tagged by version; never deleted |

---

## Skill Reference

**Skill:** `parity_scan_and_mvp_planner`
**Definition:** `.claude/skills/parity_scan_and_mvp_planner.md`
**Schema:** `.claude/contracts/schemas/parity_scan_and_mvp_planner.schema.json`
**Example:** `.claude/contracts/examples/parity_scan_and_mvp_planner_example.json`
