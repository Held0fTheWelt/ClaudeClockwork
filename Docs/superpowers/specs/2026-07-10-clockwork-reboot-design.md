# ClaudeClockwork Reboot — Design Spec

**Date:** 2026-07-10
**Status:** Approved in brainstorming session (Yves + Claude)
**Supersedes:** the entire v17.x governance/skill corpus as normative source (git history remains the archive, tag `v17-archive`)

## 1. Context & Motivation

ClaudeClockwork v17.x (last commit 2026-03-30) never worked reliably. Root causes identified:

- Process-over-product: 30+ incremental phases/MVPs produced a governance-markdown corpus (agents, protocols, escalation levels, ~95 JSON schemas, 109 manifest skills with dual dispatch) that no runtime ever enforced end-to-end.
- Hard-blocking rules (e.g. the Ollama FREEZE gate) stalled work instead of degrading gracefully.
- Ballast accumulation: ~700 MB of runtime artifacts, worktrees, duplicate Ollama directories, and four parallel documentation trees.

Meanwhile the user's methodology matured in two other projects:

- **TinyToolDevelopment (TTD):** ADR catalog with domain taxonomy, arc42 SADs with YAML frontmatter (`owns-adrs`, `uml-package`, `supersedes`), same-change design anchoring, gate tests, SAD build automation. See `/mnt/d/TinyToolDevelopment/Git/docs/ADR/README.md`.
- **Better Tomorrow / WorldOfShadows (WoS):** code-aligned UML conventions (C4 components, sequence, states; `.md` Mermaid + `.puml` companions; `TRACEABILITY.md` per package; architecture documentation gate test) and a modern AI stack (LangGraph orchestration, guarded capabilities, MCP tooling). See `/mnt/d/WorldOfShadows/UML/README.md`.

This reboot re-founds Clockwork on that methodology.

## 2. Decisions (fixed in this session)

| # | Decision |
|---|---|
| D1 | Purpose stays **multi-agent orchestration** (Claude + local Ollama models), re-founded and defined via ADR/SAD/UML instead of governance markdown. |
| D2 | **Restart in the same repo**: aggressive cut; git history is the archive (tag `v17-archive`); only selected parts are ported; ADR-CW-0001 documents the cut. |
| D3 | **Hybrid foundation**: Claude Code as orchestrator (`.claude/` agents/skills) + lean Python **MCP server** for deterministic tools + **LangGraph** pipelines (inside the MCP server) for multi-step local Ollama workflows, reusing Better Tomorrow patterns. |
| D4 | **First use case: Clockwork builds itself** — the new pipeline orchestrates its own repo cleanup, ADR/SAD creation, and UML generation. |
| D5 | **Docs language: English** for all ADR/SAD/UML artifacts; dialog with the user stays German. |
| D6 | Approach **C — Bootstrap Slice**: four short phases, each delivering working software plus anchored documentation (same-change anchoring). |
| D7 | Version restarts at **0.1.0** for the new package; the 17.x era ends at the archive tag. |

## 3. Target Architecture

```
ClaudeClockwork/
├── CLAUDE.md                # slim: entry point + pointers into ADR/SAD corpus
├── README.md, LICENSE, VERSION, pyproject.toml
├── docs/
│   ├── ADR/                 # ADR-CATALOG.md, adr-template.md, adr-cw-NNNN-<slug>.md
│   └── architecture/        # arc42 SADs with YAML frontmatter (owns-adrs, uml-package, supersedes)
│       └── core/architecture.md   # SAD-CORE: the system SAD
├── UML/                     # code-aligned UML (WoS conventions)
│   ├── README.md, _templates/c4/
│   └── Components/<slug>/{components,sequence,states}/ + TRACEABILITY.md
├── clockwork/               # NEW Python package (replaces claudeclockwork/)
│   ├── server.py            # MCP server (FastMCP, stdio)
│   ├── tools/               # deterministic: UML suite, reviewer builder, gates, repo analysis
│   └── pipelines/           # LangGraph graphs for Ollama workflows
├── .claude/                 # Claude Code layer: few agents + skills, THIN
├── .mcp.json                # registers the clockwork MCP server
└── tests/
    └── gates/               # architecture documentation gate et al.
```

### Layer 1 — Claude Code (`.claude/`)
The orchestrator. A handful of agents (e.g. architect, reviewer) and skills that call MCP tools. No governance-markdown corpus, no 109-skill registry — behavior is defined by ADRs/SADs and enforced by gate tests, not by process prose.

### Layer 2 — MCP server (`clockwork` package)
Deterministic capabilities exposed as MCP tools:
- the ported UML suite (scope catalog, repo bundle, focus bundle, diagram generate),
- the ported reviewer builder (review context, knowledge bundle, review bundle, site build, how-it-works build),
- ADR/SAD gates (link check, frontmatter check, catalog completeness, traceability check),
- repo analysis helpers.

### Layer 3 — LangGraph pipelines (same package, exposed as MCP tools)
Multi-step local-model workflows (brief; draft → review → refine) following Better Tomorrow patterns. A single runtime config `clockwork.yaml` (connection, model constraints, timeouts) carries over the one good idea of the old `local_ollama_runtime.yaml`.

### Conventions
- ADR IDs: single stream `ADR-CW-NNNN` with a domain column in the catalog. Domain-split numbering (TTD style) is deferred until the catalog needs it (YAGNI).
- SAD frontmatter follows the TTD scheme: `id`, `status`, `type`, `owns-adrs`, `uml-package`, `supersedes`, `links`.
- UML packages follow WoS minimum: `components/`, `sequence/`, `states/`, plus `README.md` and `TRACEABILITY.md`; Mermaid `.md` previews with `.puml` companions.
- ADRs must contain at least one Mermaid diagram (TTD update rule).

## 4. Inventory — port / delete

### Ported (translated into `clockwork/`, not copied verbatim)
- UML suite and reviewer builder from `.claude/skills/analysis/` (`uml_shared.py`, `uml_review_shared.py`, `repo_how_it_works_shared.py` + skill wrappers) — the March 2026 work.
- Ollama essentials: availability test, model-selection logic, constraints from `.claude/config/local_ollama_runtime.yaml` → foundation of the pipeline layer.
- Nothing else. Everything remains reachable via git history (`v17-archive`).

### Phase 0 deletions (decision-free junk, ~610 MB)
`.clockwork_runtime/`, `.worktrees/`, `claudeclockwork.zip`, `.DEPRECATED/`, `.ollama_old/`, `.ollama_from_wos/`, `.llama_runtime/`, `.pytest_cache/`, `validation_runs/`, `validation_runs_redacted/`, `cleanup_request.json`, `cleanup_run.log`, `phase6_evidence_bundle.json`, stray 37-byte `skills` file. ADR-CW-0001 documents cut + reboot decision.

### Phase 2 deletions (decision-bearing; one short ADR each)
- `.claude/` legacy corpus: 109 manifest skills, agent hierarchy, governance markdown, ~95 JSON schemas, `tasks/`, `knowledge/`, `config/` → superseded by ADR/SAD corpus + MCP tools.
- `claudeclockwork/` (old package) + old `tests/` → replaced by `clockwork/` + new gate tests.
- `mvps/`, `roadmaps/`, `.claude-development/`, `.claude-performance/`, `.clockwork_integration/`, `Docs/`, `KNOWLEDGE/`, `memory/`, `registry/`, `plugins/`, `templates/`, `demos/`, `eval/`, `scripts/`, `.project/` (surviving knowledge moves to `docs/`).
- Root markdown sprawl: `AGENTS_CATALOG.md`, `ARCHITECTURE.md`, `DEVELOPMENT.md`, `KNOWLEDGE_STRUCTURE.md`, `MODEL_POLICY.md`, `QUALITY_TRACKING.md`, `ROADMAP.md`, `Task.md`.
- `.ollama/`, `.cursor/`, `.github/`, `.wslconfig` are reviewed individually in Phase 2 (small; may contain items worth keeping such as CI config).

## 5. Self-Application Workflow ("Clockwork builds itself")

From Phase 2 on: a Claude Code agent calls the MCP tool `uml_repo_bundle` → the ported UML suite generates the UML corpus of the new repo into `UML/Components/` including `TRACEABILITY.md`. The reviewer builder produces review bundles over the new code. Every structural decision lands as ADR + catalog row **in the same change** as its implementation (same-change anchoring, TTD governance style) — a gate test enforces catalog completeness.

## 6. Error Handling

Principles carried over from TTD `SAD_Projektautomatisierung.md`:
- MCP tools are idempotent, return structured errors, and destructive operations offer a dry-run mode.
- **Ollama outage blocks nothing.** The old FREEZE rule is abolished: LangGraph pipelines degrade gracefully ("local backend unavailable" — Claude takes over or the step is skipped), deterministic tools always run.
- Drift is a red test, not a prose rule: gates run as pytest, not as governance documents.

## 7. Testing

- `tests/gates/test_architecture_documentation_gate.py` modeled on the WoS gate: every SAD frontmatter valid, every ADR in the catalog, every UML package has README + TRACEABILITY, all links resolve.
- Unit tests for MCP tools and pipeline nodes (Ollama mocked); everything non-interactive, CI-capable.

## 8. Phases & Deliverables

| Phase | Deliverable |
|---|---|
| 0 | ~610 MB junk removed, tag `v17-archive`, ADR-CW-0001 |
| 1 | Skeleton + MCP server with ported UML suite + SAD-CORE + first gate green |
| 2 | UML corpus self-generated, remaining ballast removed via mini-ADRs, repo lean |
| 3 | LangGraph/Ollama pipeline as MCP tool, anchored via ADR |

Each phase delivers working software plus anchored documentation. Phase boundaries are commit/PR boundaries.

## 9. Risks & Mitigations

- **Skeleton over-building** (the old failure mode): mitigated by YAGNI rules in this spec (single ADR stream, deferred domain split, thin `.claude/`) and by the rule that every new structure needs an ADR.
- **Ported code drags old assumptions along**: the UML/review shared modules are translated into package modules with tests, not copied with their skill-runner scaffolding.
- **Ollama/LangGraph scope creep in Phase 3**: Phase 3 starts with exactly one pipeline (draft → review → refine); further graphs need their own ADR.
- **Case-insensitive filesystem (NTFS/WSL)**: `docs/` and legacy `Docs/` are the same directory on disk; git currently tracks new files under `Docs/`. Phase 2 must delete legacy `Docs/` *content* selectively (keeping `superpowers/specs/` and the new corpus) and then `git mv` the tracked paths to lowercase `docs/` in a dedicated commit.
