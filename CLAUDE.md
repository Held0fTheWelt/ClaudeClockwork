# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

**Clockwork** — a meta-governance and tooling layer for multi-agent Claude/Ollama orchestration. The `.claude/` directory is the system core (agent roles, governance protocols, skill runners, JSON contracts). The `.project/` directory holds project-operational files for working on Clockwork itself. When deploying Clockwork on another project, `.project/` contents move to that project's root.

## Commands

### System Tools

```bash
# Test Ollama availability (run at start of session or after Ollama restart)
python3 .claude/tools/test_ollama.py

# Check Ollama status manually
curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin)['models']]"

# Run a skill tool
python3 .claude/tools/skills/skill_runner.py <skill_name> [args]

# Ollama briefing
echo "task description" | python3 .claude/tools/ollama_brief.py [model] [type]
# Types: brief | draft | architecture | review | quick
```

## Development

### Setup & Verification

```bash
# Verify complete environment setup (boot check)
python3 .claude/tools/boot_check.py

# Test Ollama availability (optional, needed only for L2+ tasks)
python3 .claude/tools/test_ollama.py
```

### Running the CLI

```bash
# Show help
python3 -m claudeclockwork.cli --help

# Run a skill through the manifest system
python3 -m claudeclockwork.cli --skill-id <skill_name> --inputs '{...}'

# Example: build capability map
python3 -m claudeclockwork.cli --skill-id capability_map_build --inputs '{}'
```

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run a specific test
python3 -m pytest tests/test_full_skill_system_smoke.py::test_registry_discovers_manifest_skills -v

# Run with coverage
python3 -m pytest tests/ --cov=claudeclockwork
```

### Code Structure

**Main package:** `claudeclockwork/` — contains CLI entry point (`cli.py`), runtime builder (`runtime.py`), manifest bridge (`bridge.py`), and core modules:
- `core/base` — foundational types and interfaces
- `core/executor` — execution pipeline and task runners
- `core/planner` — planning and routing logic
- `core/registry` — skill registry discovery
- `core/models` — data models and contracts
- `core/security` — security validation

**System core:** `.claude/` (never deploy as application code) — agent definitions, governance rules, skill implementations, JSON schemas, and Ollama integration tools.

**Project workspace:** `.project/` — documentation, plans, reviews, memory across sessions.

## Execution Protocol

Always read in this order at session start:
1. `CLAUDE.md` + `.claude/SYSTEM.md` — project identity and module hierarchy
2. `.project/MEMORY.md` — stable cross-session knowledge
3. `.claude/governance/workflow_triggers.md` — trigger routing and document naming

### Workflow Trigger Keywords

| Keyword | Workflow | Document output |
|---|---|---|
| **Task:** | Plan creation | `.project/Docs/Plans/Plan_<Name>.md` |
| **Review:** | Review creation | `.project/Docs/Review/Review_<Name>.md` |
| **Critics:** | Fundamental critique | `.project/Docs/Critics/Critics_<Severity>_<Name>.md` |
| **Implement:** | Execute a plan | Code changes |
| **Archive:** | Archive completed task (BP-005) | `.project/Docs/References/`, `.project/Docs/Documentation/`, `.claude/knowledge/index.md` |
| **test ollama** | Ollama health check | (no document) |

### Escalation Levels

| Level | Decision authority | Typical situation |
|---|---|---|
| L0 | Specialist autonomous | 1 file, no API change |
| L1 | Team Lead | 2-5 files, clear boundaries |
| L2 | Architecture Agent | New module, new dependency |
| L3 | Technical Critic | Performance paths, external API |
| L4 | Systemic Critic | Governance changes, new agent types |
| **L5** | **User — STOP and ask** | Orchestrator redesign, backend switch |

**Ollama gate:** L0 = skip Ollama. L1 = optional (recommended for >50 lines). L2+ = mandatory. If Ollama is called and unavailable → FREEZE (no partial implementation).

## Architecture

### Directory Structure

```
.claude/                  # Clockwork system core (SSoT) — never deploy-target
  agents/                 # Agent role definitions
    critics/              # Technical + Systemic critic definitions
    learning/             # Per-agent learning logs
    operations/           # Ops-level agents (bulk planner, skill scout)
    testops/              # Test orchestration agents
    workers/              # Implementation + report workers
    docs/                 # Documentation pipeline agents
    analysis/             # Pattern, mutation, system map agents
    meta/                 # Skill discovery + forge agents
    quality/              # Batch validator, local verifier
  contracts/              # JSON schemas + SPEC_SHEET.md (SSoT for data contracts)
    schemas/              # ~95 JSON Schema files for all inter-agent specs
  governance/             # Execution protocol, routing matrix, policies
  tasks/                  # Task templates organized by domain
    input/                # Message triad building
    planning/             # Plan compaction, mutation, lint
    qa/                   # QA gate runs
    ops/                  # Drift sentinel, capability map, release cut
    skills/               # Skill-specific task files
  tools/                  # Deterministic Python tools + skill runners
    skills/               # Individual skill scripts (one per skill)
  skills/                 # Skill documentation (registry, playbooks, per-skill READMEs)
    playbooks/            # Multi-skill campaign playbooks
  knowledge/              # Librarian-managed knowledge base + index
  python/                 # Python architecture + pattern standards
  config/                 # YAML/JSON config (pricing, budgeting, routing)

.project/                 # Project-operational files (this project = Clockwork dev)
  MEMORY.md               # Cross-session knowledge (SSoT — read first each session)
  ARCHITECTURE.md         # System design for this project
  ROADMAP.md              # Active milestones
  MODEL_POLICY.md         # Model tier overrides
  QUALITY_TRACKING.md     # Telemetry + stats
  memory/                 # Team Lead cross-session context files
  Docs/
    Plans/                # Task descriptions + implementation plans
    Review/               # Validation reports
    Critics/              # Critic outputs
    Documentation/        # Technical docs
    References/           # Archived reference documents
    Tutorials/            # Guides
```

### Agent Hierarchy

```
Orchestrator (Team Lead)  — routes, orchestrates, never implements directly
├── SpecialAgents (Departments) — build packs, normalize results, small context
│   ├── Implementation Agent (src/ owner on deployment target)
│   ├── Architecture Agent / Designer
│   ├── Documentation Agent (.project/Docs/Documentation/, Tutorials/)
│   ├── Librarian Agent (.project/Docs/References/, .claude/knowledge/)
│   ├── Validation Agent (.project/Docs/Review/)
│   └── Critics: Technical (L3) + Systemic (L4)
└── Workers (Execution Plane) — receive Pack + TasklistSpec, not full conversation
```

### Pipeline Flow

```
Message → TasklistSpec → RoutingSpec → PackManifest (+Pack) → WorkerResult → ReportSpec/QualitySignal → CriticReport (optional) → OpsLedgerSummary
```

### Contracts (`.claude/contracts/schemas/`)

All inter-agent data uses typed JSON specs. Key schemas:
- `tasklist_spec` — output of Task Compactor
- `routing_spec` — output of Personaler/Team Lead
- `pack_manifest` — output of Content Packer
- `report_spec` / `quality_signal` — output of Report Worker
- `critic_report` — output of Critics
- `testreport_spec` — output of TestOps

Trust modes: `inherit` (default, uses Pack), `verify` (adds Goal/Constraints), `rebuild` (re-reads original, expensive).

### Model Routing

**Escalation order: Oodle tier first, then Claude tier.** Opus 4.6 (C4) is disabled by default.

| Claude Tier | Model | Use case |
|---|---|---|
| C0 | Claude 4/4.1 | Admin, dispatch, checklists |
| C1 | Haiku 4.5 | Task compaction, quick reviews |
| C2 | Sonnet 4.5 | Implementation, diff-based fixes |
| C3 | Sonnet 4.6 | High-risk fixes, final arch decisions |
| C4 | Opus 4.6 | Manual only |

| Oodle Tier | Models | Use case |
|---|---|---|
| S (7-14b) | `qwen2.5-coder:14b`, `phi4:14b` (GPU) | Routing, reviews, architecture |
| M (32-33b) | `qwen2.5-coder:32b` (CPU) | Implementation drafts |
| L (70-72b) | `qwen2.5:72b`, `llama3.3:70b` (CPU) | Hard reasoning, briefings |

Hardware: RTX 3080 (10 GB VRAM) for ≤14b GPU models; 7950X3D / 64 GB DDR5 for CPU-only models. Hybrid (model split across VRAM+RAM) is slower than pure CPU — avoid.

## Key Governance Rules

- **No silent architecture changes.** Core decisions require user confirmation.
- **File ownership is strict.** No agent edits another agent's files — use Domain Handoff via Team Lead.
- **Team Lead does not write code or files directly** — delegates all implementation via Task tool.
- **Governance Trinity:** `specialists.md` + `execution_protocol.md` + `.project/MEMORY.md` must always be updated together when a new agent is integrated.
- **German narrative input workflow:** build a `MessageTriadSpec` first (`.claude/tasks/input/000_BUILD_MESSAGE_TRIAD.md`), then work from `work_brief`.
- **Drift Sentinel hard stop:** if `contract_drift_sentinel` FAILs, stop and fix before proceeding.
- **QA gate** before risky work: `.claude/tasks/qa/000_RUN_QA_GATE.md`.
- **Token budgeting** is enabled by default (`.claude/config/performance_budgeting.yaml`). Finalize with `performance_finalize` skill.

## Document Naming Convention

```
<Prefix>_<TopicPascalCase>.md
```

| Type | Prefix | Location |
|---|---|---|
| Plan | `Plan_` | `.project/Docs/Plans/` |
| Review | `Review_` | `.project/Docs/Review/` |
| Critic (minor) | `Critics_Minor_` | `.project/Docs/Critics/` |
| Critic (normal) | `Critics_Normal_` | `.project/Docs/Critics/` |
| Critic (major) | `Critics_Major_` | `.project/Docs/Critics/` |
| Reference | `Ref_` | `.project/Docs/References/` |

Related documents share the same topic part: `Plan_OllamaClient.md`, `Review_OllamaClient.md`, `Critics_Normal_OllamaClient.md`.
