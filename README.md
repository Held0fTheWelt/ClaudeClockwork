# Clockwork

**Meta-governance and tooling layer for multi-agent Claude/Ollama orchestration.**

Clockwork is a comprehensive framework for autonomous AI agent orchestration, providing structured governance, deterministic skills, and a robust contract system for coordinating multiple AI models (Claude API and local Ollama models).

**Current Version:** See [.claude/VERSION](.claude/VERSION). Phases 0–61 complete (see [roadmaps/Roadmap_ClockworkV18.md](roadmaps/Roadmap_ClockworkV18.md)).

---

## What Is Clockwork?

Clockwork solves the challenge of **coordinating multiple AI agents** working on complex software tasks. Instead of relying on unstructured AI conversations, Clockwork provides:

- **Governance Protocols** — Clear escalation paths, file ownership rules, and decision policies
- **Agent Hierarchy** — Structured roles from Team Lead to specialized workers
- **Deterministic Skills** — 109+ manifest skills plus direct-runner tool scripts
- **JSON Contracts** — Typed inter-agent communication specifications (~95 schemas)
- **Local-First Architecture** — Ollama models handle bulk work; Claude handles coordination

### Key Design Principles

1. **Local-First (Ollama)** — Use local LLMs for drafts, reviews, and analysis; escalate to Claude only when needed
2. **Small-First Model Selection** — Start with the cheapest capable model; escalate tier before switching providers
3. **Strict File Ownership** — Each agent owns specific files; cross-domain changes require formal handoff
4. **Contracts Over Free Text** — All inter-agent data uses typed JSON specs for reproducibility

---

## Quick Start

### 1. Verify Environment

```bash
python3 .claude/tools/boot_check.py
```

Expected output: `[PASS]` or `[FAIL]` per check, ending with `Result: ALL CHECKS PASSED`.

### 2. Test Ollama (Optional)

```bash
python3 .claude/tools/test_ollama.py
```

Ollama is recommended for L2+ tasks (architecture decisions, new modules). If unavailable, the freeze protocol applies.

### 3. First Run (create runtime root)

```bash
python3 -m claudeclockwork.cli first-run --project-root .
```

### 4. Run a Skill

```bash
# Manifest CLI (109 skills, registry-based)
python3 -m claudeclockwork.cli --project-root . --skill-id <skill_name> --inputs '{}'

# Direct runner (scripting / .claude/tools/skills/)
python3 .claude/tools/skills/skill_runner.py <skill_name> [args]
```

### 6. Run Tests

```bash
python3 -m pytest tests/ -v
```

---

## Architecture Overview

### Directory Structure

```
.claude/                  # System Core (SSoT) — governance, agents, contracts, skills
  agents/                 # Agent role definitions
    critics/              # Technical + Systemic critic definitions
    learning/             # Per-agent learning logs
    operations/           # Ops-level agents (bulk planner, skill scout)
    testops/              # Test orchestration agents
    workers/              # Implementation + report workers
    docs/                 # Documentation pipeline agents
  contracts/              # JSON schemas (~95) + SPEC_SHEET.md
  governance/             # Execution protocol, routing, policies
  skills/                 # Skill documentation + playbooks
  tools/                  # Python tools + skill runners
    skills/               # Individual skill scripts
  knowledge/              # Librarian-managed knowledge base
  config/                 # YAML/JSON configuration

.project/                 # Project Workspace
  MEMORY.md               # Cross-session knowledge (SSoT)
  ARCHITECTURE.md         # System design
  ROADMAP.md              # Milestones
  Docs/                   # Plans, Reviews, Critics, Documentation

claudeclockwork/          # Python Package
  cli/                    # CLI (main, first-run, env-check, migrate, ops, plugin)
  runtime.py              # Runtime builder
  bridge.py               # Manifest bridge
  core/                   # Executor, planner, registry, gates, autopilot
  cas/                    # Content-addressed store, smart cache
  workgraph/              # Work graph engine, cross-project
  scheduler/              # Job queue, priorities, telemetry
  plugins/                # Loader, registry, signing, certification, publish
  migrations/             # Config/schema migration engine
  workspace/              # Policy resolver, dependency graph, federation
  optimizer/              # Cost model, calibration, telemetry
  workers/                # Dispatcher, local worker, remote stub

mvps/                     # MVP Phase Documentation (Phases 0–61)
docs/                     # Platform docs (see Docs/INDEX.md)
roadmaps/                 # Roadmap_ClockworkV18.md
```

### Agent Hierarchy

```
Orchestrator (Team Lead)
├── SpecialAgents (Departments)
│   ├── Implementation Agent — writes/modifies code
│   ├── Architecture Agent / Designer — module structure, dependencies
│   ├── Documentation Agent — technical docs, tutorials
│   ├── Librarian Agent — knowledge base, references
│   ├── Validation Agent — syntax check, tests, reviews
│   ├── Collector Agent — correctness validation
│   ├── Pattern Recognition Agent — reusable abstractions
│   └── Skill Agent — meta-advisor for efficiency
├── Critics (Quality Gates)
│   ├── Technical Critic (L3) — performance, runtime risks
│   └── Systemic Critic (L4) — governance, long-term complexity
└── Workers (Execution Plane)
    ├── Implementation Worker
    └── Report Worker
```

### Escalation Levels

| Level | Decision Authority | Typical Situation |
|---|---|---|
| L0 | Specialist autonomous | 1 file, no API change |
| L1 | Team Lead | 2-5 files, clear boundaries |
| L2 | Architecture Agent | New module, new dependency |
| L3 | Technical Critic | Performance paths, external API |
| L4 | Systemic Critic | Governance changes, new agent types |
| **L5** | **User — STOP and ask** | Orchestrator redesign, backend switch |

### Model Routing

**Escalation order: Local Model tier first, then Claude tier.**

| Tier | Claude Model | Use Case |
|---|---|---|
| C0 | Claude 4/4.1 | Admin, dispatch, checklists |
| C1 | Haiku 4.5 | Task compaction, quick reviews |
| C2 | Sonnet 4.5 | Implementation, diff-based fixes |
| C3 | Sonnet 4.6 | High-risk fixes, final architecture decisions |
| C4 | Opus 4.6 | Manual only (disabled by default) |

| Tier | Local Models | Use Case |
|---|---|---|
| S (7-14b) | qwen2.5-coder:14b, phi4:14b | Routing, reviews, architecture |
| M (32-33b) | qwen2.5-coder:32b | Implementation drafts |
| L (70-72b) | qwen2.5:72b, llama3.3:70b | Hard reasoning, briefings |

---

## Skill System

Clockwork includes **90+ deterministic skills** — tool-first micro-workflows that execute without LLM calls:

### Core Skills

| Skill | Description |
|---|---|
| `repo_validate` | Check repository consistency (broken links, invalid JSON) |
| `spec_validate` | Validate JSON specs against schemas |
| `qa_gate` | PR-blocking QA checks (drift, topology, SSoT) |
| `evidence_bundle_build` | Build reproducible evidence bundles |
| `contract_drift_sentinel` | Detect schema/example drift |

### Documentation Skills

| Skill | Description |
|---|---|
| `doc_write` | Deterministic documentation file writer |
| `tutorial_write` | Tutorial renderer with section validation |
| `doc_review` | Doc lint (TODOs, missing sections, broken links) |
| `pdf_render` | High-quality PDF from Markdown |
| `pdf_quality` | Quality rubric scorer for manuscripts |

### Analysis Skills

| Skill | Description |
|---|---|
| `pattern_detect` | Detect recurring code patterns |
| `system_map` | Heuristic module dependency map |
| `code_assimilate` | Draft integration plans for foreign code |
| `mutation_detect` | Compare snapshots, detect renames/moves |

### Routing & Budgeting Skills

| Skill | Description |
|---|---|
| `budget_router` | Deterministic cost/latency budgeting |
| `model_routing_select` | Cheapest model selector |
| `escalation_router` | Automatic escalation on failures |
| `work_scope_assess` | Workload/effort assessment |

### Cleanup Skills

| Skill | Description |
|---|---|
| `repo_clean_scan` | Find junk artifacts, duplicates |
| `code_clean_scan` | Find orphan modules, markers |
| `cleanup_plan_apply` | Apply cleanup plans (archive-first) |

### Skill Dispatch

| System | Entry Point | Skills | Description |
|--------|-------------|-------|-------------|
| **Manifest CLI** | `python3 -m claudeclockwork.cli --project-root . --skill-id <skill>` | 109 | Registry discovers `.claude/skills/**/manifest.json`; run any registered skill. |
| **Direct runner** | `python3 .claude/tools/skills/skill_runner.py <skill>` | ~100+ | Runs skill scripts in `.claude/tools/skills/` directly (e.g. for scripting). |

---

## Governance

### Workflow Triggers

| Keyword | Workflow | Output |
|---|---|---|
| **Task:** | Plan creation | `.project/Docs/Plans/Plan_<Name>.md` |
| **Review:** | Review creation | `.project/Docs/Review/Review_<Name>.md` |
| **Critics:** | Fundamental critique | `.project/Docs/Critics/Critics_<Severity>_<Name>.md` |
| **Implement:** | Execute a plan | Code changes |
| **Archive:** | Task archival (BP-005) | References, Documentation, Index |
| **test ollama** | Health check | (no document) |

### Key Rules

1. **No silent architecture changes** — Core decisions require user confirmation
2. **File ownership is strict** — Use Domain Handoff via Team Lead for cross-domain changes
3. **Team Lead does not write code** — Delegates all implementation via Task tool
4. **Ollama gate** — L0 skips Ollama; L1+ requires Ollama briefing; unavailable = FREEZE
5. **Governance Trinity** — `specialists.md` + `execution_protocol.md` + `MEMORY.md` update together
6. **Drift Sentinel** — If `contract_drift_sentinel` FAILs, stop and fix before proceeding

### Pipeline Flow

```
Message → TasklistSpec → RoutingSpec → PackManifest (+Pack) → WorkerResult → ReportSpec/QualitySignal → CriticReport (optional) → OpsLedgerSummary
```

---

## Contract System

All inter-agent communication uses typed JSON specs (~95 schemas in `.claude/contracts/schemas/`):

| Contract | Producer | Purpose |
|---|---|---|
| TasklistSpec | Task Compactor | Structured task briefing |
| RoutingSpec | Personaler/Team Lead | Agent + model assignment |
| PackManifest | Content Packer | Minimal context bundle |
| ReportSpec | Report Worker | Execution results |
| QualitySignal | Report Worker | Compact routing signal |
| CriticReport | Critics | Adversarial review |
| TestReportSpec | TestOps | Test results |

### Trust Modes

- `inherit` — Worker trusts TasklistSpec + Pack (default)
- `verify` — Adds Goal/Constraints extract (10-20 lines)
- `rebuild` — Re-reads original message (expensive)

---

## MVP Roadmap

Clockwork development follows a phased MVP approach. **Phases 0–61 are complete.** Each phase has a dedicated MVP document in [mvps/](mvps/):

| Phase | Name | MVP |
|-------|------|-----|
| 0 | Foundation & Cleanup | [MVP_Phase0](mvps/MVP_Phase0_FoundationCleanup.md) |
| 1 | Manifest Hardening | [MVP_Phase1](mvps/MVP_Phase1_ManifestHardening.md) |
| 2 | Wrapper Wave 3 | [MVP_Phase2](mvps/MVP_Phase2_WrapperWave3.md) |
| 3 | Native Core Services | [MVP_Phase3](mvps/MVP_Phase3_NativeCoreServices.md) |
| 4 | Plugin Runtime | [MVP_Phase4](mvps/MVP_Phase4_PluginRuntime.md) |
| 5 | MCP Layer | [MVP_Phase5](mvps/MVP_Phase5_MCPLayer.md) |
| 6 | CI / Eval / Quality Gates | [MVP_Phase6](mvps/MVP_Phase6_CIEvalGates.md) |
| 7 | Wrapper Wave 4 (Legacy CLI Gap) | [MVP_Phase7](mvps/MVP_Phase7_WrapperWave4.md) |
| 8 | Code & Governance Hygiene | [MVP_Phase8](mvps/MVP_Phase8_CodeHygiene.md) |
| 9 | Test Hardening | [MVP_Phase9](mvps/MVP_Phase9_TestHardening.md) |
| 10 | Compaction & Pluggability | [MVP_Phase10](mvps/MVP_Phase10_Compaction.md) |
| 11 | Legacy Doc Migration | [MVP_Phase11](mvps/MVP_Phase11_LegacyDocMigration.md) |
| 12 | Duplicate Elimination | [MVP_Phase12](mvps/MVP_Phase12_DuplicateElimination.md) |
| 13 | Greenfield Content Update | [MVP_Phase13](mvps/MVP_Phase13_GreenfieldUpdate.md) |
| 14 | Native Skill Promotion | [MVP_Phase14](mvps/MVP_Phase14_NativeSkills.md) |
| 15 | Obsolete Data Prune | [MVP_Phase15](mvps/MVP_Phase15_ObsoleteDataPrune.md) |
| 16 | Skill Discovery Wave | [MVP_Phase16](mvps/MVP_Phase16_SkillDiscovery.md) |
| 17 | Adapter Elimination | [MVP_Phase17](mvps/MVP_Phase17_AdapterElimination.md) |
| 18 | Planning Drift Guard & Single Source of Truth | [MVP_Phase18](mvps/MVP_Phase18_PlanningDriftGuard.md) |
| 18F | Re-Audit from MVP 18 (Quality Gates Baseline) | [MVP_Phase18F](mvps/MVP_Phase18F_ReAuditFromMVP18.md) |
| 18G | Version & Pointer Consistency | [MVP_Phase18G](mvps/MVP_Phase18G_VersionPointerConsistency.md) |
| 18H | `.report/` Curated-Only + Runtime Migration | [MVP_Phase18H](mvps/MVP_Phase18H_ReportCuratedOnly_RuntimeMigration.md) |
| 18I | Skill Coverage Repair + Registry Sync | [MVP_Phase18I](mvps/MVP_Phase18I_SkillCoverageRepair_ChangelogEntry.md) |
| 18J | Gate Stabilization & Green Run (RC Minimum) | [MVP_Phase18J](mvps/MVP_Phase18J_GreenRunRC.md) |
| 19 | Runtime Root Normalization | [MVP_Phase19](mvps/MVP_Phase19_RuntimeRootNormalization.md) |
| 20 | Local Non-LLM Tooling (LocalAI) v1 | [MVP_Phase20](mvps/MVP_Phase20_LocalNonLLMTooling.md) |
| 21 | Adapter Elimination Accelerator | [MVP_Phase21](mvps/MVP_Phase21_AdapterEliminationAccelerator.md) |
| 22 | Release Discipline & Upgrade Pipeline | [MVP_Phase22](mvps/MVP_Phase22_ReleaseDiscipline_UpgradePipeline.md) |
| 23 | Evidence & Redaction Pipeline | [MVP_Phase23](mvps/MVP_Phase23_EvidenceRedactionPipeline.md) |
| 24 | Tool/Model Governance (Capability Policy 2.0) | [MVP_Phase24](mvps/MVP_Phase24_ToolModelGovernance_CapabilityPolicy2.md) |
| 25 | Eval Harness v2 (Scoreboards, Trends) | [MVP_Phase25](mvps/MVP_Phase25_EvalHarnessV2_Scoreboards.md) |
| 26 | Router v3 (Bandit + Budget Toggle) | [MVP_Phase26](mvps/MVP_Phase26_RouterV3_BanditBudget.md) |
| 27 | Adapter Elimination at Scale | [MVP_Phase27](mvps/MVP_Phase27_AdapterEliminationAtScale.md) |
| 28 | Distribution & Installation (Packaging) | [MVP_Phase28](mvps/MVP_Phase28_DistributionPackaging.md) |
| 29 | Plugin Marketplace / Extension API | [MVP_Phase29](mvps/MVP_Phase29_PluginExtensionAPI.md) |
| 30 | Work Graph Engine (Tasks as DAG) | [MVP_Phase30](mvps/MVP_Phase30_WorkGraphEngine.md) |
| 31 | Learning Layer (Router + Policy Training) | [MVP_Phase31](mvps/MVP_Phase31_LearningLayer.md) |
| 32 | Observability (Telemetry, Debug, Forensics) | [MVP_Phase32](mvps/MVP_Phase32_Observability.md) |
| 33 | Multi-Repo / Multi-Project Orchestration | [MVP_Phase33](mvps/MVP_Phase33_MultiRepoWorkspaces.md) |
| 34 | Security Hardening & Sandboxing | [MVP_Phase34](mvps/MVP_Phase34_SecurityHardening_Sandboxing.md) |
| 35 | Distributed Workers (Remote Execution) | [MVP_Phase35](mvps/MVP_Phase35_DistributedWorkers.md) |
| 36 | Deterministic Caching & CAS | [MVP_Phase36](mvps/MVP_Phase36_ContentAddressedStore.md) |
| 37 | Workspace UX & Project Templates | [MVP_Phase37](mvps/MVP_Phase37_WorkspaceUX_ProjectTemplates.md) |
| 38 | Knowledge Base Layer | [MVP_Phase38](mvps/MVP_Phase38_KnowledgeBaseLayer.md) |
| 39 | Reliability Engineering (Chaos, Recovery) | [MVP_Phase39](mvps/MVP_Phase39_ReliabilityEngineering.md) |
| 40 | Plugin Ecosystem v2 (Signing, Compatibility) | [MVP_Phase40](mvps/MVP_Phase40_PluginEcosystemV2.md) |
| 41 | Performance & Cost Optimizer | [MVP_Phase41](mvps/MVP_Phase41_PerfCostOptimizer.md) |
| 42 | Operational UX v2 (Incidents, Dashboards) | [MVP_Phase42](mvps/MVP_Phase42_OperationalUXv2.md) |
| 43 | Multi-Repo Orchestrator v2 | [MVP_Phase43](mvps/MVP_Phase43_MultiRepoOrchestratorV2.md) |
| 44 | Stable Public Surface (CLI/API, SemVer) | [MVP_Phase44](mvps/MVP_Phase44_StablePublicSurface.md) |
| 45 | Documentation Suite v2 (Runbooks, Troubleshooting) | [MVP_Phase45](mvps/MVP_Phase45_DocumentationSuiteV2.md) |
| 46 | One-Command Demo Pipelines | [MVP_Phase46](mvps/MVP_Phase46_OneCommandDemoPipelines.md) |
| 47 | Community/Registry Ready | [MVP_Phase47](mvps/MVP_Phase47_RegistryReadyPlugins.md) |
| 48 | Scheduler v2 (Queues, Priorities, Fairness) | [MVP_Phase48](mvps/MVP_Phase48_SchedulerV2.md) |
| 49 | Cost Model Calibration | [MVP_Phase49](mvps/MVP_Phase49_CostModelCalibration.md) |
| 50 | Smart Caching (Cross-Project, Safe Sharing) | [MVP_Phase50](mvps/MVP_Phase50_SmartCaching_CrossProject.md) |
| 51 | SLO Autopilot (Self-Healing Policies) | [MVP_Phase51](mvps/MVP_Phase51_SLOAutopilot.md) |
| 52 | Repo Refactor & Module Boundaries | [MVP_Phase52](mvps/MVP_Phase52_RepoRefactor_ModuleBoundaries.md) |
| 53 | Test Pyramid Upgrade (Unit → Integration → E2E) | [MVP_Phase53](mvps/MVP_Phase53_TestPyramidUpgrade.md) |
| 54 | Migration System (Config/Schema Migrations) | [MVP_Phase54](mvps/MVP_Phase54_MigrationSystem.md) |
| 55 | Operator Toolkit (CLI/TUI, Quick Ops) | [MVP_Phase55](mvps/MVP_Phase55_OperatorToolkit.md) |
| 56 | Workspace Federation v2 (Policies per Project) | [MVP_Phase56](mvps/MVP_Phase56_WorkspaceFederationV2_PoliciesPerProject.md) |
| 57 | Cross-Repo Dependency Graph | [MVP_Phase57](mvps/MVP_Phase57_CrossRepoDependencyGraph.md) |
| 58 | Inter-Project Pipelines | [MVP_Phase58](mvps/MVP_Phase58_InterProjectPipelines.md) |
| 59 | Plugin Certification (Quality Tiers) | [MVP_Phase59](mvps/MVP_Phase59_PluginCertification.md) |
| 60 | Remote Worker Fleet (Networking + Auth) | [MVP_Phase60](mvps/MVP_Phase60_RemoteWorkerFleet.md) |
| 61 | Marketplace UX (Local Registry UI) | [MVP_Phase61](mvps/MVP_Phase61_MarketplaceUX_LocalRegistryUI.md) |

See **[roadmaps/Roadmap_ClockworkV18.md](roadmaps/Roadmap_ClockworkV18.md)** for detailed phase descriptions and current state.

---

## Documentation

### For Humans

- [ARCHITECTURE.md](ARCHITECTURE.md) — Project architecture, runtime layout
- [ROADMAP.md](ROADMAP.md) — Milestones (see also [roadmaps/Roadmap_ClockworkV18.md](roadmaps/Roadmap_ClockworkV18.md))
- [MODEL_POLICY.md](MODEL_POLICY.md) — Model tiers and triggers
- [.project/MEMORY.md](.project/MEMORY.md) — Cross-session context
- [QUALITY_TRACKING.md](QUALITY_TRACKING.md) — Quality tracking
- [Docs/INDEX.md](Docs/INDEX.md) — Platform docs index (runbooks, troubleshooting, contracts)

### For Claude/Agents

- [CLAUDE.md](CLAUDE.md) — Session start, protocol, workflow triggers
- [.claude/SYSTEM.md](.claude/SYSTEM.md) — System architecture, agent hierarchy
- [.claude/INDEX.md](.claude/INDEX.md) — Entry point for .claude context

### Skills

- [.claude/skills/registry.md](.claude/skills/registry.md) — Full skill catalog
- [.claude/skills.md](.claude/skills.md) — Pointer to registry and playbooks
- [.claude/skills/playbooks/](.claude/skills/playbooks/) — Multi-skill campaign playbooks

---

## Prerequisites

- **Python 3.10+** — For boot check, skill runner, CLI, and tools
- **Ollama** (optional) — Recommended for L2+ tasks; local inference endpoint at `localhost:11434`

### Hardware Recommendations (for Ollama)

| Device | Models |
|---|---|
| RTX 3080 (10 GB VRAM) | ≤14b models (phi4:14b, qwen2.5-coder:14b) |
| 64 GB RAM | 32-72b models (qwen2.5-coder:32b, llama3.3:70b) |

**Note:** Hybrid mode (VRAM+RAM split) is slower than pure CPU — avoid.

---

## Commands Reference

### System Tools

```bash
# Boot check
python3 .claude/tools/boot_check.py

# Test Ollama
python3 .claude/tools/test_ollama.py

# Ollama briefing
echo "task description" | python3 .claude/tools/ollama_brief.py [model] [type]
# Types: brief | draft | architecture | review | quick
```

### CLI

```bash
# Show help
python3 -m claudeclockwork.cli --help

# First-run, env-check
python3 -m claudeclockwork.cli --project-root . first-run
python3 -m claudeclockwork.cli --project-root . env-check

# Run skill via manifest system
python3 -m claudeclockwork.cli --project-root . --skill-id <skill_name> --inputs '{}'

# Migrate config (dry-run / apply)
python3 -m claudeclockwork.cli --project-root . migrate [--dry-run | --apply]

# Operator toolkit (bundles, plugins, budget, cache, graph, impact)
python3 -m claudeclockwork.cli --project-root . ops <bundles|plugins|budget|cache|graph|impact>

# Plugin marketplace (search, info, install, update, uninstall)
python3 -m claudeclockwork.cli --project-root . plugin search [--query ...]
python3 -m claudeclockwork.cli --project-root . plugin info <plugin_id>

# Run work graph
python3 -m claudeclockwork.cli.run_graph demos/smoke/graph.json --project-root .
```

### Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test
python3 -m pytest tests/test_full_skill_system_smoke.py::test_registry_discovers_manifest_skills -v

# Run with coverage
python3 -m pytest tests/ --cov=claudeclockwork
```

### Skills (Examples)

```bash
# Repository validation
python3 .claude/tools/skills/skill_runner.py repo_validate

# QA gate (PR-blocking checks)
python3 .claude/tools/skills/skill_runner.py qa_gate

# Build evidence bundle
python3 .claude/tools/skills/skill_runner.py evidence_bundle_build

# Document review
python3 .claude/tools/skills/skill_runner.py doc_review '{"target_path": "docs/"}'
```

---

## Current State

- **Phases 0–61** are complete (see [roadmaps/Roadmap_ClockworkV18.md](roadmaps/Roadmap_ClockworkV18.md) and [mvps/](mvps/)).
- **Skill dispatch:** Manifest CLI (109 skills, registry-based) and direct runner for scripting.
- **Stable surface:** CLI contract, public API map, SemVer policy, and compatibility tests in [Docs/](Docs/) (cli_contract.md, public_api.md, semver_policy.md).
- **Operator toolkit:** `clockwork ops` (bundles, plugins, budget, cache, graph, impact) and `clockwork plugin` (search, info, install, update, uninstall).
- **Demo pipelines:** One-command demos under `demos/smoke`, `demos/gate_pipeline`, `demos/incident_export`.

---

## Contributing

### Adding a New Skill

1. Create skill script in `.claude/tools/skills/<skill_name>.py`
2. Add JSON schema in `.claude/contracts/schemas/<skill_name>.schema.json`
3. Add example in `.claude/contracts/examples/<skill_name>_example.json`
4. Register in `.claude/skills/registry.md`
5. (Optional) Add manifest in `.claude/skills/<skill_name>/manifest.json` for CLI access

### Governance Updates

When modifying governance, update all three Trinity files together:
- `.claude/agents/specialists.md`
- `.claude/governance/execution_protocol.md`
- `.project/MEMORY.md`

---

## License

See [LICENSE](LICENSE) for details.

---

## Acknowledgments

Clockwork evolved from the Llama Code / Oodle Code projects, incorporating lessons from multi-agent orchestration research and practical deployment experience.
