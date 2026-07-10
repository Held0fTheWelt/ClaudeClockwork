# ClaudeClockwork Reboot — Master Plan (Overview)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild ClaudeClockwork as an ADR/SAD/UML-anchored multi-agent orchestration toolkit (Claude Code orchestrator + MCP tool server + LangGraph local-model pipelines), removing ~700 MB of legacy ballast in the process.

**Spec:** `docs/superpowers/specs/2026-07-10-clockwork-reboot-design.md` (approved 2026-07-10)

**Architecture:** Three layers — (1) thin `.claude/` Claude Code layer, (2) `clockwork/` Python package exposing deterministic tools (UML suite, reviewer builder, gates) via a FastMCP stdio server, (3) LangGraph pipelines for local Ollama workflows inside the same package. All decisions anchored as ADRs consolidated into arc42 SADs, validated by pytest gate tests.

**Tech Stack:** Python ≥3.10, `mcp` (FastMCP), PyYAML, pytest; Phase 3 adds `langgraph>=1.0.3,<2` and `httpx`.

## Global Constraints

These apply to **every task in every phase plan**:

- All project artifacts (docs, code, comments, commit messages) in **English**. Dialog with the user is German.
- Python floor: `requires-python = ">=3.10"` (host has 3.10.12).
- New package is `clockwork/`; the PyPI project name stays `claudeclockwork`; version restarts at `0.1.0`.
- ADR IDs: single stream `ADR-CW-NNNN`, files `docs/ADR/adr-cw-NNNN-<slug>.md`, every ADR registered in `docs/ADR/ADR-CATALOG.md` **in the same commit** (same-change anchoring) and containing at least one ` ```mermaid ` block.
- SAD frontmatter keys (YAML): `id`, `status`, `type`, `owns-adrs`, `uml-package`, `links`.
- The filesystem is **case-insensitive** (NTFS/WSL): never create a path that differs from an existing one only by case. After Phase 0 Task 0.2 the docs tree is tracked as lowercase `docs/`.
- No FREEZE semantics anywhere: local-model unavailability degrades gracefully, deterministic tools always run.
- Commit at the end of every task; git history is the archive (tag `v17-archive`).
- Working branch: `reboot/bootstrap-slice`.

## Phase Plans (execute in order)

| # | Plan file | Deliverable |
|---|---|---|
| 0 | `2026-07-10-reboot-phase0-cut-and-adr.md` | ~610 MB junk removed, tag `v17-archive`, ADR corpus scaffolded, ADR-CW-0001 |
| 1 | `2026-07-10-reboot-phase1-skeleton-mcp.md` | `clockwork/` package with ported UML suite + reviewer builder, FastMCP server, SAD-CORE, first gate green |
| 2 | `2026-07-10-reboot-phase2-self-application.md` | Legacy corpus removed via mini-ADRs, UML corpus self-generated, repo lean, full suite green |
| 3 | `2026-07-10-reboot-phase3-local-pipelines.md` | LangGraph draft→review→refine pipeline on local Ollama as MCP tool, anchored via ADR + SAD |

Each phase ends with working, testable software. Phase boundaries are commit-series boundaries on the reboot branch; do not start phase N+1 with phase N's verification failing.

## Verification at each phase end

```bash
python3 -m pytest tests/gates/ -v          # architecture documentation gate (Phase 1+)
python3 -m pytest tests/clockwork/ -v      # unit tests for the new package (Phase 1+)
python3 -m pytest tests/ -v                # full suite (Phase 2+, after legacy test removal)
```
