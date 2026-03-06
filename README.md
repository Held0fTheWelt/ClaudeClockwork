# Clockwork

**Meta-governance and tooling layer for multi-agent Claude/Ollama orchestration.**

Clockwork is a comprehensive framework for autonomous AI agent orchestration, providing structured governance, deterministic skills, and a robust contract system for coordinating multiple AI models (Claude API and local Ollama models).

**Current Version:** 17.7.28 (see [.claude/VERSION](.claude/VERSION))

---

## What Is Clockwork?

Clockwork solves the challenge of **coordinating multiple AI agents** working on complex software tasks. Instead of relying on unstructured AI conversations, Clockwork provides:

- **Governance Protocols** — Clear escalation paths, file ownership rules, and decision policies
- **Agent Hierarchy** — Structured roles from Team Lead to specialized workers
- **Deterministic Skills** — 90+ tool-first micro-workflows that reduce token usage
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

### 3. Run a Skill

```bash
# Legacy runner (97 skills)
python3 .claude/tools/skills/skill_runner.py <skill_name> [args]

# Manifest CLI (34 skills with registry discovery)
python3 -m claudeclockwork.cli --skill-id <skill_name> --inputs '{}'
```

### 4. Run Tests

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
  cli.py                  # CLI entry point
  runtime.py              # Runtime builder
  bridge.py               # Manifest bridge
  core/                   # Core modules (executor, planner, registry)

mvps/                     # MVP Phase Documentation (16 phases)
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

### Two Dispatch Systems

| System | Entry Point | Skills | Description |
|---|---|---|---|
| Legacy Runner | `python3 .claude/tools/skills/skill_runner.py <skill>` | 97 | Direct function dispatch |
| Manifest CLI | `python3 -m claudeclockwork.cli --skill-id <skill>` | 34 | Registry-discovered manifests |

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

Clockwork development follows a phased MVP approach:

| Phase | Focus |
|---|---|
| 0 | Foundation Cleanup |
| 1 | Manifest Hardening |
| 2 | Wrapper Wave 3 |
| 3 | Native Core Services |
| 4 | Plugin Runtime |
| 5 | MCP Layer |
| 6 | CI Eval Gates |
| 7 | Wrapper Wave 4 |
| 8 | Code Hygiene |
| 9 | Test Hardening |
| 10 | Compaction |
| 11 | Legacy Doc Migration |
| 12 | Duplicate Elimination |
| 13-15 | Greenfield, Native Skills, Skill Discovery |

See `mvps/` directory for detailed phase documentation.

---

## Documentation

### For Humans

- [ARCHITECTURE.md](ARCHITECTURE.md) — Project architecture, runtime layout
- [ROADMAP.md](ROADMAP.md) — Phases and milestones
- [MODEL_POLICY.md](MODEL_POLICY.md) — Model tiers and triggers
- [MEMORY.md](MEMORY.md) — Cross-session context
- [QUALITY_TRACKING.md](QUALITY_TRACKING.md) — Quality tracking

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

# Run skill via manifest system
python3 -m claudeclockwork.cli --skill-id <skill_name> --inputs '{}'

# Build capability map
python3 -m claudeclockwork.cli --skill-id capability_map_build --inputs '{}'
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
