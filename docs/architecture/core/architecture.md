---
id: SAD-CW-CORE
status: accepted
type: project-sad
owns-adrs:
  - ADR-CW-0002
uml-package: UML/Components/clockwork-core
links:
  - ../../ADR/ADR-CATALOG.md
  - ../../../UML/README.md
---

# Clockwork Core - Software Architecture (arc42, project-wide)

**System:** Clockwork core (MCP tool server + analysis tools)
**Scope:** package layout, tool surface, gate integrity, porting boundary
**Last reconciled:** 2026-07-10

## 1. Introduction & Goals

Clockwork provides architecture-anchored orchestration tooling: repository
analysis and UML generation, review bundles, documentation gates, and (from
Phase 3) local-model pipelines. Every structural decision is an ADR; this
SAD is the durable home of the core decisions and owns ADR-CW-0002.

## 2. Constraints

- Python >= 3.10; dependencies limited to `mcp`, `pyyaml` (core) and
  `langgraph`/`httpx` (optional `local` extra).
- Case-insensitive filesystem: no paths differing only by case.
- All artifacts English.

## 3. Context & Scope

Claude Code (or any MCP client) connects over stdio to the `clockwork`
server (`.mcp.json`). The server operates on a target repository passed as
`repo_root` - Clockwork itself is the first target (self-application).

## 4. Solution Strategy

Ported v17 analysis core (`uml_shared`, `uml_review_shared`,
`how_it_works_shared`) wrapped by plain bundle functions
(`clockwork/tools/bundles.py`) and exposed 1:1 as MCP tools
(`clockwork/server.py`). Gates (`clockwork/tools/gates.py`) are consumed by
pytest (normative) and by the `architecture_gate` MCP tool (convenience).

## 5. Building Block View

| Module | Responsibility |
|---|---|
| `clockwork/tools/uml_shared.py` | repo scan, dependency resolution, PlantUML/Mermaid rendering |
| `clockwork/tools/uml_review_shared.py` | review context payloads + static review site |
| `clockwork/tools/how_it_works_shared.py` | how-it-works guide payloads |
| `clockwork/tools/bundles.py` | seven bundle builder functions (public API) |
| `clockwork/tools/gates.py` | architecture documentation gate |
| `clockwork/server.py` | FastMCP server exposing tools |
| `clockwork/pipelines/` | Phase 3: LangGraph local pipelines |

## 6. Architecture Decisions

Owned: ADR-CW-0002 (three-layer architecture). Related: ADR-CW-0001
(reboot and cut, owned by governance history, not consolidated).

## 7. Quality & Testing

`tests/clockwork/` unit-tests every public function against fixture
repositories; `tests/gates/test_architecture_documentation_gate.py` runs the
gate against this repository and must stay green.
