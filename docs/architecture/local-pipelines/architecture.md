---
id: SAD-CW-LOCAL
status: accepted
type: project-sad
owns-adrs:
  - ADR-CW-0007
uml-package: UML/Components/clockwork-pipelines
links:
  - ../../ADR/ADR-CATALOG.md
  - ../core/architecture.md
---

# Local Pipelines - Software Architecture (arc42)

**System:** local-model pipeline layer (`clockwork/pipelines/`)
**Scope:** runtime config, Ollama client, LangGraph graphs, MCP exposure,
degradation policy
**Last reconciled:** 2026-07-10

## 1. Introduction & Goals

Give Claude Code cheap local drafting/review capacity without ever blocking
deterministic work. Owns ADR-CW-0007.

## 2. Constraints

- Optional `local` extra (`langgraph>=1.0.3,<2`, `httpx>=0.27`); core install
  stays independent (lazy imports in `clockwork/server.py`).
- GPU-first model constraints are data in `clockwork.yaml` (default
  `qwen3:8b`, fallback `phi4`, forbidden 32B/70B/72B).

## 3. Building Block View

| Module | Responsibility |
|---|---|
| `clockwork/pipelines/runtime.py` | `RuntimeConfig`, `load_runtime_config`, `OllamaClient` (health, generate, 404-fallback, forbidden-model guard) |
| `clockwork/pipelines/briefs.py` | single-step `run_brief` |
| `clockwork/pipelines/draft_review_refine.py` | LangGraph draft->review->refine graph |
| `clockwork/server.py` (local tools) | `local_health`, `local_brief`, `local_draft_review_refine` |

## 4. Runtime View

Primary and degraded paths: see
[UML/Components/clockwork-pipelines/sequence/pipeline_paths.md](../../../UML/Components/clockwork-pipelines/sequence/pipeline_paths.md).
Degradation contract: unreachable backend returns
`{"status": "local_backend_unavailable"}` - callers (Claude) decide how to
proceed; no retries, no blocking.

## 5. Quality & Testing

Unit tests are network-free (`tests/clockwork/test_pipelines_runtime.py`,
`test_pipelines_graph.py`, server degradation test). The only live test is
`tests/clockwork/test_integration_local.py` (`integration` marker,
self-skipping).
