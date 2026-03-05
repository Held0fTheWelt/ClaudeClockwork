# MASTER PROMPT — Claude Code Execution Contract

This repository is a structured, multi-agent setup.

## Non‑Negotiables
- Work through **Specs/Contracts** in `.claude/contracts/`.
- Routing follows `.claude/governance/routing_matrix.md` and `.claude/governance/model_escalation_policy.md`.
- Prefer **small-first** models. Escalate **Oodle tier first**, then **Claude tier**.

## Standard Flow
1) Task Compactor produces `TasklistSpec`
2) Content Packer produces `PackManifest` + Packs
3) Workers execute tasks and produce `ResultSpec` / `ReportSpec`
4) TestOps runs deterministic tests; LLMs triage only
5) Critic validates where required; Team_Lead decides escalation
6) Ops Ledger records the run and proposes cost/quality improvements

## Trust Modes
- inherit / verify / rebuild — see `.claude/contracts/SPEC_SHEET.md`

## Output Requirements
- Any report must include a `QualitySignal` if errors were found.
- Any test claim must include or reference a `TestReportSpec`.
