# Clockwork v18 Roadmap

**Baseline:** v17.7.0 — 94 legacy skills, 34 manifest skills (28 adapters + 6 native), 5 passing tests
**Current:** v18.3+ — Phases 0–61 complete; stable public surface, docs suite v2, demo pipelines, registry ready, scheduler v2, cost calibration, smart caching, SLO autopilot, module boundaries, test pyramid, migrations, ops toolkit, workspace federation v2, dependency graph, inter-project pipelines, plugin certification, remote worker stubs, marketplace UX
**Sources:** skill_system_audit_and_roadmap.md · skill_system_legacy_migration_matrix.md · mvps/MVP_Phase*.md
**Updated:** 2026-03-07

---

## Phase Overview

| Phase | Name | Status | MVP |
|-------|------|--------|-----|
| 0 | Foundation & Cleanup | **Complete** | [MVP_Phase0](../mvps/MVP_Phase0_FoundationCleanup.md) |
| 1 | Manifest Hardening | **Complete** | [MVP_Phase1](../mvps/MVP_Phase1_ManifestHardening.md) |
| 2 | Wrapper Wave 3 | **Complete** | [MVP_Phase2](../mvps/MVP_Phase2_WrapperWave3.md) |
| 3 | Native Core Services | **Complete** | [MVP_Phase3](../mvps/MVP_Phase3_NativeCoreServices.md) |
| 4 | Plugin Runtime | **Complete** | [MVP_Phase4](../mvps/MVP_Phase4_PluginRuntime.md) |
| 5 | MCP Layer | **Complete** | [MVP_Phase5](../mvps/MVP_Phase5_MCPLayer.md) |
| 6 | CI / Eval / Quality Gates | **Complete** | [MVP_Phase6](../mvps/MVP_Phase6_CIEvalGates.md) |
| 7 | Wrapper Wave 4 (Legacy CLI Gap) | **Complete** | [MVP_Phase7](../mvps/MVP_Phase7_WrapperWave4.md) |
| 8 | Code & Governance Hygiene | **Complete** | [MVP_Phase8](../mvps/MVP_Phase8_CodeHygiene.md) |
| 9 | Test Hardening | **Complete** | [MVP_Phase9](../mvps/MVP_Phase9_TestHardening.md) |
| 10 | Compaction & Pluggability | **Complete** | [MVP_Phase10](../mvps/MVP_Phase10_Compaction.md) |
| 11 | Legacy Doc Migration | **Complete** | [MVP_Phase11](../mvps/MVP_Phase11_LegacyDocMigration.md) |
| 12 | Duplicate Elimination | **Complete** | [MVP_Phase12](../mvps/MVP_Phase12_DuplicateElimination.md) |
| 13 | Greenfield Content Update | **Complete** | [MVP_Phase13](../mvps/MVP_Phase13_GreenfieldUpdate.md) |
| 14 | Native Skill Promotion | **Complete** | [MVP_Phase14](../mvps/MVP_Phase14_NativeSkills.md) |
| 15 | Obsolete Data Prune | **Complete** | [MVP_Phase15](../mvps/MVP_Phase15_ObsoleteDataPrune.md) |
| 16 | Skill Discovery Wave | **Complete** | [MVP_Phase16](../mvps/MVP_Phase16_SkillDiscovery.md) |
| 17 | Adapter Elimination | **Complete** | [MVP_Phase17](../mvps/MVP_Phase17_AdapterElimination.md) |
| 18 | Planning Drift Guard & Single Source of Truth | **Complete** | [MVP_Phase18](../mvps/MVP_Phase18_PlanningDriftGuard.md) |
| 18F | Re-Audit from MVP 18 (Quality Gates Baseline) | **Complete** | [MVP_Phase18F](../mvps/MVP_Phase18F_ReAuditFromMVP18.md) |
| 18G | Version & Pointer Consistency | **Complete** | [MVP_Phase18G](../mvps/MVP_Phase18G_VersionPointerConsistency.md) |
| 18H | `.report/` Curated-Only + Runtime Migration | **Complete** | [MVP_Phase18H](../mvps/MVP_Phase18H_ReportCuratedOnly_RuntimeMigration.md) |
| 18I | Skill Coverage Repair + Registry Sync | **Complete** | [MVP_Phase18I](../mvps/MVP_Phase18I_SkillCoverageRepair_ChangelogEntry.md) |
| 18J | Gate Stabilization & Green Run (RC Minimum) | **Complete** | [MVP_Phase18J](../mvps/MVP_Phase18J_GreenRunRC.md) |
| 19 | Runtime Root Normalization | **Complete** | [MVP_Phase19](../mvps/MVP_Phase19_RuntimeRootNormalization.md) |
| 20 | Local Non-LLM Tooling (LocalAI) v1 | **Complete** | [MVP_Phase20](../mvps/MVP_Phase20_LocalNonLLMTooling.md) |
| 21 | Adapter Elimination Accelerator | **Complete** | [MVP_Phase21](../mvps/MVP_Phase21_AdapterEliminationAccelerator.md) |
| 22 | Release Discipline & Upgrade Pipeline | **Complete** | [MVP_Phase22](../mvps/MVP_Phase22_ReleaseDiscipline_UpgradePipeline.md) |
| 23 | Evidence & Redaction Pipeline | **Complete** | [MVP_Phase23](../mvps/MVP_Phase23_EvidenceRedactionPipeline.md) |
| 24 | Tool/Model Governance (Capability Policy 2.0) | **Complete** | [MVP_Phase24](../mvps/MVP_Phase24_ToolModelGovernance_CapabilityPolicy2.md) |
| 25 | Eval Harness v2 (Scoreboards, Trends) | **Complete** | [MVP_Phase25](../mvps/MVP_Phase25_EvalHarnessV2_Scoreboards.md) |
| 26 | Router v3 (Bandit + Budget Toggle) | **Complete** | [MVP_Phase26](../mvps/MVP_Phase26_RouterV3_BanditBudget.md) |
| 27 | Adapter Elimination at Scale | **Complete** | [MVP_Phase27](../mvps/MVP_Phase27_AdapterEliminationAtScale.md) |
| 28 | Distribution & Installation (Packaging) | **Complete** | [MVP_Phase28](../mvps/MVP_Phase28_DistributionPackaging.md) |
| 29 | Plugin Marketplace / Extension API | **Complete** | [MVP_Phase29](../mvps/MVP_Phase29_PluginExtensionAPI.md) |
| 30 | Work Graph Engine (Tasks as DAG) | **Complete** | [MVP_Phase30](../mvps/MVP_Phase30_WorkGraphEngine.md) |
| 31 | Learning Layer (Router + Policy Training) | **Complete** | [MVP_Phase31](../mvps/MVP_Phase31_LearningLayer.md) |
| 32 | Observability (Telemetry, Debug, Forensics) | **Complete** | [MVP_Phase32](../mvps/MVP_Phase32_Observability.md) |
| 33 | Multi-Repo / Multi-Project Orchestration | **Complete** | [MVP_Phase33](../mvps/MVP_Phase33_MultiRepoWorkspaces.md) |
| 34 | Security Hardening & Sandboxing | **Complete** | [MVP_Phase34](../mvps/MVP_Phase34_SecurityHardening_Sandboxing.md) |
| 35 | Distributed Workers (Remote Execution) | **Complete** | [MVP_Phase35](../mvps/MVP_Phase35_DistributedWorkers.md) |
| 36 | Deterministic Caching & CAS | **Complete** | [MVP_Phase36](../mvps/MVP_Phase36_ContentAddressedStore.md) |
| 37 | Workspace UX & Project Templates | **Complete** | [MVP_Phase37](../mvps/MVP_Phase37_WorkspaceUX_ProjectTemplates.md) |
| 38 | Knowledge Base Layer | **Complete** | [MVP_Phase38](../mvps/MVP_Phase38_KnowledgeBaseLayer.md) |
| 39 | Reliability Engineering (Chaos, Recovery) | **Complete** | [MVP_Phase39](../mvps/MVP_Phase39_ReliabilityEngineering.md) |
| 40 | Plugin Ecosystem v2 (Signing, Compatibility) | **Complete** | [MVP_Phase40](../mvps/MVP_Phase40_PluginEcosystemV2.md) |
| 41 | Performance & Cost Optimizer | **Complete** | [MVP_Phase41](../mvps/MVP_Phase41_PerfCostOptimizer.md) |
| 42 | Operational UX v2 (Incidents, Dashboards) | **Complete** | [MVP_Phase42](../mvps/MVP_Phase42_OperationalUXv2.md) |
| 43 | Multi-Repo Orchestrator v2 | **Complete** | [MVP_Phase43](../mvps/MVP_Phase43_MultiRepoOrchestratorV2.md) |
| 44 | Stable Public Surface (CLI/API, SemVer) | **Complete** | [MVP_Phase44](../mvps/MVP_Phase44_StablePublicSurface.md) |
| 45 | Documentation Suite v2 (Runbooks, Troubleshooting) | **Complete** | [MVP_Phase45](../mvps/MVP_Phase45_DocumentationSuiteV2.md) |
| 46 | One-Command Demo Pipelines | **Complete** | [MVP_Phase46](../mvps/MVP_Phase46_OneCommandDemoPipelines.md) |
| 47 | Community/Registry Ready | **Complete** | [MVP_Phase47](../mvps/MVP_Phase47_RegistryReadyPlugins.md) |
| 48 | Scheduler v2 (Queues, Priorities, Fairness) | **Complete** | [MVP_Phase48](../mvps/MVP_Phase48_SchedulerV2.md) |
| 49 | Cost Model Calibration | **Complete** | [MVP_Phase49](../mvps/MVP_Phase49_CostModelCalibration.md) |
| 50 | Smart Caching (Cross-Project, Safe Sharing) | **Complete** | [MVP_Phase50](../mvps/MVP_Phase50_SmartCaching_CrossProject.md) |
| 51 | SLO Autopilot (Self-Healing Policies) | **Complete** | [MVP_Phase51](../mvps/MVP_Phase51_SLOAutopilot.md) |
| 52 | Repo Refactor & Module Boundaries | **Complete** | [MVP_Phase52](../mvps/MVP_Phase52_RepoRefactor_ModuleBoundaries.md) |
| 53 | Test Pyramid Upgrade (Unit → Integration → E2E) | **Complete** | [MVP_Phase53](../mvps/MVP_Phase53_TestPyramidUpgrade.md) |
| 54 | Migration System (Config/Schema Migrations) | **Complete** | [MVP_Phase54](../mvps/MVP_Phase54_MigrationSystem.md) |
| 55 | Operator Toolkit (CLI/TUI, Quick Ops) | **Complete** | [MVP_Phase55](../mvps/MVP_Phase55_OperatorToolkit.md) |
| 56 | Workspace Federation v2 (Policies per Project) | **Complete** | [MVP_Phase56](../mvps/MVP_Phase56_WorkspaceFederationV2_PoliciesPerProject.md) |
| 57 | Cross-Repo Dependency Graph | **Complete** | [MVP_Phase57](../mvps/MVP_Phase57_CrossRepoDependencyGraph.md) |
| 58 | Inter-Project Pipelines | **Complete** | [MVP_Phase58](../mvps/MVP_Phase58_InterProjectPipelines.md) |
| 59 | Plugin Certification (Quality Tiers) | **Complete** | [MVP_Phase59](../mvps/MVP_Phase59_PluginCertification.md) |
| 60 | Remote Worker Fleet (Networking + Auth) | **Complete** | [MVP_Phase60](../mvps/MVP_Phase60_RemoteWorkerFleet.md) |
| 61 | Marketplace UX (Local Registry UI) | **Complete** | [MVP_Phase61](../mvps/MVP_Phase61_MarketplaceUX_LocalRegistryUI.md) |

**Principle:** No big-bang rewrites. Each phase delivers a working, tested increment. Legacy runner stays operational throughout.

---

## Current State Snapshot (v17.7.0)

### Skill inventory

| Layer | Count | State |
|-------|-------|-------|
| Legacy Python modules (`.claude/tools/skills/`) | 94 | Operational — 91 runnable, 2 internal helpers, 1 bridge |
| Manifest-wrapped skills (`.claude/skills/`) | 34 | Partially integrated — 28 adapters, 6 native |
| Reference prompt skills (`SKILL.md`) | 17 | Planned/prompt-level only |
| Plugin skeletons (`plugins/`) | 2 | Scaffolded — no loader |
| Tests | 5 | All passing |

### Skill reachability gap

63 legacy skills have **no manifest** and are **only reachable via `skill_runner.py`**, not via `python3 -m claudeclockwork.cli`. Migration is tracked in `Docs/skill_system_legacy_migration_matrix.md`.

### Known drift (audit 2026-03-06)

| ID | Issue | Blocking? |
|----|-------|-----------|
| C3 | Manifest entrypoint namespace (`skills.*` vs `bundle.*`) — dormant risk | Phase 1 |
| F1 | Plugin system has no Python loader | Phase 4 |
| S1 | "Oodle Tier" naming stale in governance + skill code | Phase 0 |
| D1 | ~170 files still contain German content | Phase 0 |

---

## Phase 0 — Foundation & Cleanup

**Goal:** Clear all blocking drift and language violations before building new functionality.
**Status:** Complete (2026-03-06).

### Remaining tasks

| Task | Priority | Owner |
|------|----------|-------|
| Fix manifest entrypoint namespace (C3) | Blocking | Implementation Agent |
| Translate 39 agent definition files in `.claude/agents/` | Critical | Documentation Agent |
| Translate 15 governance files in `.claude/governance/` | Critical | Documentation Agent |
| Translate 106 skill README files in `.claude/skills/` | High | Documentation Agent |
| Rename "Oodle Tier" → "Local Model Tier" in governance + skill code | High | Implementation Agent |
| Update `.claude/INDEX.md` stale path references | Medium | Documentation Agent |
| Remove stale `llamacode` import attempts in `bandit_router_select.py`, `escalation_router.py` | Medium | Implementation Agent |
| Populate `.project/MEMORY.md` with findings from 2026-03-06 audit | Medium | Team Lead |
| Clarify `Docs/` vs `.project/Docs/` — consolidate or document split | Low | Team Lead |
| Remove or update `SRC_ORIGIN_RULE.md` to match actual `claudeclockwork/` package | Low | Implementation Agent |

### Done in Phase 0

- [x] `.report/` directory created (boot check fix)
- [x] Root `VERSION` file created
- [x] `ARCHITECTURE.md` updated — removed `llamacode/`, `oodle/`, `src/`
- [x] `README.md` translated to English
- [x] `ROADMAP.md` translated to English
- [x] `MEMORY.md` translated to English
- [x] `.claude/SYSTEM.md` translated to English
- [x] Skill dispatch split documented in `CLAUDE.md`
- [x] `.clockwork_runtime/eval/results/` created

---

## Phase 1 — Manifest Hardening

**Goal:** Make the manifest/registry system production-reliable. Fix the entrypoint namespace issue. Enforce schema contracts.
**Prerequisite:** Phase 0 entrypoint fix complete.

### Deliverables

1. **Entrypoint namespace fix** — update all 34 manifests or fix `loader.py` so `SkillLoader.load_skill_class()` can resolve actual paths without relying on `LegacySkillAdapter` bypass.
2. **Manifest schema** — formalize required fields (`id`, `name`, `description`, `version`, `entrypoint`, `permissions`) using JSON Schema or Pydantic model.
3. **`manifest_validate` extension** — add import-path resolution check and schema validation (currently only checks field presence).
4. **Categories, tags, aliases, permissions normalized** — all 34 manifests use consistent taxonomy.
5. **Tests** — add test that loads each manifest and verifies entrypoint resolves without error.

### Acceptance criteria

- `manifest_validate` returns `valid=true` AND successfully imports each skill class
- No `ModuleNotFoundError` when loading any of the 34 manifests via `SkillLoader`
- New skill added via manifest scaffold passes `manifest_validate` on first attempt

---

## Phase 2 — Wrapper Wave 3

**Goal:** Bring the next 11 high-priority legacy skills into the manifest system.
**Prerequisite:** Phase 1 complete (manifests must be reliably loadable).

### Skills to wrap (P1 from migration matrix)

| Skill | Category | Notes |
|-------|----------|-------|
| `determinism_proof` | qa | High-value SHA256 verification |
| `hardening_scan_fix` | qa | Security hardening scanner |
| `drift_semantic_check` | qa | Cross-file semantic drift detection |
| `team_topology_verify` | qa | Agent hierarchy validation |
| `reference_fix` | docs | Backtick path fixer |
| `outcome_event_generate` | evidence | Artifact pipeline — outcome events |
| `outcome_ledger_append` | evidence | Artifact pipeline — ledger writer |
| `clockwork_version_bump` | misc | Version bump utility |
| `telemetry_summarize` | performance | Token/cost summarizer |
| `performance_toggle` | performance | Budgeting on/off toggle |
| `performance_finalize` | performance | Export performance report |

### Deliverables per skill

- `manifest.json` (id, name, description, version, category, permissions, entrypoint)
- `skill.py` (subclass of `LegacySkillAdapter`, or native if trivially rewritable)
- Test coverage: at least one assertion beyond `status == "ok"`

### Acceptance criteria

- All 11 skills discoverable via `python3 -m claudeclockwork.cli --skill-id <skill>`
- `capability_map_build` reports 45 manifest skills (34 + 11)
- All tests pass

---

## Phase 3 — Native Core Services

**Goal:** Rewrite the most critical meta and QA skills as native implementations — not legacy adapters.
**Prerequisite:** Phase 2 complete.

### First wave (meta/registry)

| Skill | Rationale |
|-------|-----------|
| `skill_registry_search` | Powers all skill discovery — should not depend on legacy subprocess |
| `skill_scaffold` | Creates new skills — must understand manifest format natively |
| `capability_map_build` | Core observability — must reflect live registry state natively |

### Second wave (QA gates)

| Skill | Rationale |
|-------|-----------|
| `repo_validate` | Runs before risky work — must be reliable |
| `spec_validate` | Contract validation — must be schema-aware |
| `qa_gate` | Pre-commit gate — must be fast and dependency-free |

### Third wave (artifact/evidence pipeline)

| Skill | Rationale |
|-------|-----------|
| `evidence_bundle_build` | Core evidence artifact — rich enough to skip legacy |
| `security_redactor` | Security-sensitive — should not depend on subprocess reliability |
| `parity_scan_and_mvp_planner` | Planning skill — high value for agent workflows |
| `eval_run` | Evaluation harness — needs direct registry access |
| `pdf_quality` | Document pipeline — benefits from native template system |

### Deliverables per skill

- Native `skill.py` (no `LegacySkillAdapter`) with full logic inline or via `claudeclockwork.core.*`
- Unit tests for the skill's core logic (not just `status == "ok"`)
- `manifest.json` updated if needed

### Acceptance criteria

- All listed skills execute end-to-end without calling into `skill_runner.py`
- Each has at least 2 unit tests covering real behavior
- Skill logic is importable from `claudeclockwork.*` without side effects

---

## Phase 4 — Plugin Runtime

**Goal:** Wire the existing plugin JSON scaffolds into a live Python plugin loader.
**Prerequisite:** Phase 3 complete (native skills must be stable before plugin boundary is drawn).

### Deliverables

1. **`claudeclockwork/core/plugin/loader.py`** — discovers `plugins/*/plugin.json`, validates schema, registers capabilities.
2. **`claudeclockwork/core/plugin/registry.py`** — tracks installed plugins, enable/disable state (persisted to `registry/plugin_index.json`).
3. **`claudeclockwork/core/plugin/dependency.py`** — resolves skill ↔ plugin dependencies; blocks execution if required plugin not enabled.
4. **Lifecycle hooks** — `on_install`, `on_enable`, `on_disable`, `healthcheck` as optional keys in `plugin.json`.
5. **`build_executor()` integration** — `runtime.py` loads plugins before building executor.
6. **Tests** — plugin discovery, enable/disable toggle, dependency validation failure.

### Acceptance criteria

- `plugin_registry_export` reports plugin state that matches enabled/disabled state on disk
- Skill that declares a plugin dependency fails cleanly if that plugin is disabled
- `boot_check.py` passes with plugin registry loaded

---

## Phase 5 — MCP Layer

**Goal:** Expose Clockwork skills and resources via the Model Context Protocol without creating a hard dependency on MCP.
**Prerequisite:** Phase 4 complete (plugin runtime defines the boundary of what is exposed).

### Deliverables

1. **MCP client adapter** — thin wrapper so Clockwork can call external MCP servers.
2. **Local STDIO MCPs** — `filesystem` and `git` plugin.json wired to real STDIO MCP servers.
3. **MCP tool export** — selected native skills exported as MCP Tools (at minimum: `skill_registry_search`, `qa_gate`, `manifest_validate`).
4. **MCP resources** — reference skills (`SKILL.md` assets) exposed as MCP Resources.
5. **MCP prompts** — major workflow playbooks exposed as MCP Prompts.

### Acceptance criteria

- `python3 -m claudeclockwork.mcp` starts an STDIO MCP server
- At least 3 native skills callable as MCP tools
- MCP layer is optional — removing it does not break the core CLI

---

## Phase 6 — CI / Eval / Quality Gates

**Goal:** Make the skill system permanently verifiable through automated gates.
**Prerequisite:** Phases 1–5 provide enough manifest coverage to make gates meaningful.

### Deliverables

| Gate | What it checks |
|------|---------------|
| Manifest lint | All `manifest.json` files pass schema validation |
| Import lint | All entrypoints resolve without `ModuleNotFoundError` |
| Permission lint | All permissions declared in manifests exist in `configs/permissions.json` |
| Smoke run | Each wrapped skill returns `status == "ok"` with minimal inputs |
| Registry export diff | `capability_map_build` output matches previous run (no silent additions/removals) |
| Plugin index diff | `plugin_registry_export` output stable across runs |
| Capability map diff | Skill count, categories, and tags stable across runs |

### Deliverables

- `pytest` test suite covering all gates above
- CI config (GitHub Actions or equivalent) running gate suite on every commit
- `eval_run` skill integrated with `.clockwork_runtime/eval/results/` for per-run snapshots
- Registry export stored in `.clockwork_runtime/` as baseline for diff gate

### Acceptance criteria

- All 6 gates pass on clean checkout
- A manifest with a bad entrypoint fails the import lint gate
- A skill removed from registry is caught by the registry export diff gate

---

## Skills not yet in any phase (P2 keep_legacy)

These 60 skills are in the legacy runner only and have no phase assignment yet. They remain reachable via `skill_runner.py`. Reassess after Phase 3 when native patterns are established.

**Routing** (6): `bandit_router_select`, `budget_router`, `escalation_router`, `model_routing_select`, `model_routing_record_outcome`, `route_autotune_suggest`, `route_profile_patch_pack`, `route_profile_update`

**Planning** (11): `create_mvp`, `creativity_burst`, `decision_feedback`, `deliberation_pack_build`, `economics_regression`, `edge_case_selector`, `hypothesis_builder`, `idea_dedupe`, `idea_scoring`, `plan_diff_apply`, `plan_lint`, `plan_mutate`, `triad_build`, `triad_ref_lint`, `work_scope_assess`

**Analysis** (5): `code_assimilate`, `limitation_harvest_scan`, `mechanic_explain`, `mutation_detect`, `pattern_detect`, `system_map`

**Docs** (8): `autodocs_generate`, `copyright_standardize`, `doc_review`, `doc_ssot_resolver`, `doc_write`, `pdf_export`, `reference_fix`, `screencast_script`, `tutorial_write`

**Performance** (3): `budget_analyze`, `performance_finalize`, `performance_toggle`, `telemetry_summarize`, `token_event_log`

**Archive** (3): `last_train`, `last_train_merge`, `shadow_prompt`, `shadow_prompt_minify`

**Misc** (5): `clockwork_version_bump`, `critics_board_review`, `efficiency_review`, `exec_dryrun`, `log_standardize`, `prompt_debt_capture`, `review_panel`

**Demo/retire** (3): `hello`, `report`, `scan`

---

## Phases 18–61 at a glance

| Phase | Goal (one line) |
|-------|------------------|
| 18–18J | Planning drift guard, re-audit, version consistency, report/runtime migration, skill coverage, green run RC |
| 19 | Runtime root normalization (`.clockwork_runtime/`) |
| 20–29 | LocalAI, adapter acceleration, release/upgrade, evidence/redaction, capability policy, eval v2, router v3, adapter at scale, packaging, plugin extension API |
| 30–39 | Work graph engine, learning layer, observability, multi-repo, security/sandboxing, distributed workers, CAS, workspace UX, knowledge base, reliability |
| 40–43 | Plugin ecosystem v2, cost optimizer, operational UX v2, multi-repo orchestrator v2 |
| 44–54 | Stable public surface, docs v2, demo pipelines, registry ready, scheduler v2, cost calibration, smart caching, SLO autopilot, module boundaries, test pyramid, migration system |
| 55–61 | Operator toolkit, workspace federation v2, dependency graph, inter-project pipelines, plugin certification, remote worker fleet, marketplace UX |

---

## Recommended session order

1. Phase 0 remaining tasks (language migration, entrypoint fix)
2. Phase 1 (manifest hardening — unblocks all further phases)
3. Phase 2 (wrapper wave 3 — widens CLI coverage)
4. Phase 3 (native rewrites — removes adapter debt)
5. Phase 4 (plugin runtime — enables MCP boundary)
6. Phase 5 (MCP layer)
7. Phase 6 (CI gates — seal quality permanently)
8. Phases 7–17 (hygiene, test hardening, compaction, discovery, adapter elimination)
9. Phases 18–61 (see Phase Overview table and MVP links above)
