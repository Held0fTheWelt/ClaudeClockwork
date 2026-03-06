# Clockwork

Meta-governance and tooling layer for multi-agent Claude/Ollama orchestration. The system core is in `.claude/`: agent roles, governance protocols, skill runners, and JSON contracts. Application code lives in `claudeclockwork/` (project-specific).

---

## Quick Start

Verify environment (boot check):

```bash
python3 .claude/tools/boot_check.py
```

Expected output: `[PASS]` or `[FAIL]` per line, ending with `Result: ALL CHECKS PASSED`.

Optional — test Ollama availability:

```bash
python3 .claude/tools/test_ollama.py
```

Run a skill:

```bash
python3 .claude/tools/skills/skill_runner.py <skill_name> [args]
```

---

## Version & Status

- **Version:** see [.claude/VERSION](.claude/VERSION) (currently 17.7.0).
- **Roadmap:** [ROADMAP.md](ROADMAP.md) — phases, CBL-Rung, next milestones.

---

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `.claude/` | System core: agents, governance, skills, contracts |
| `Docs/` | Living documentation (plans, reviews, critics, references, tutorials) |
| `memory/` | Cross-session context (Team Lead) |
| `.report/` | Reports (canonical) |
| `.llama_runtime/` | Runtime state (ledgers, eval, writes) |
| `.claude-performance/` | Telemetry and performance artifacts |

Details: [ARCHITECTURE.md](ARCHITECTURE.md), [CLAUDE.md](CLAUDE.md).

---

## Further Documentation

**For humans:**

- [ARCHITECTURE.md](ARCHITECTURE.md) — project architecture, runtime layout
- [ROADMAP.md](ROADMAP.md) — phases and milestones
- [MODEL_POLICY.md](MODEL_POLICY.md) — model tiers and triggers
- [MEMORY.md](MEMORY.md) — cross-session context
- [QUALITY_TRACKING.md](QUALITY_TRACKING.md) — quality tracking

**For Claude/agents:**

- [CLAUDE.md](CLAUDE.md) — session start, protocol, workflow triggers
- [.claude/SYSTEM.md](.claude/SYSTEM.md) — system architecture, agent hierarchy
- [.claude/INDEX.md](.claude/INDEX.md) — entry point in the .claude context (entry docs, boot check)

**Skills:**

- [.claude/skills/registry.md](.claude/skills/registry.md) — skill catalog
- [.claude/skills.md](.claude/skills.md) — pointer to registry and playbooks

---

## Prerequisites

- **Python 3** for boot check, skill runner, and tools.
- **Ollama** is optional; recommended for L2+ tasks (e.g. architecture, new modules). If a task uses Ollama and Ollama is unreachable, the freeze protocol applies (no partial implementation). See [CLAUDE.md](CLAUDE.md) and `.claude/governance/ollama_integration.md`.

---

## Full Skill System

In addition to the legacy runner, there is now a manifest-based skill system. The canonical manifest set currently lives in `.claude/skills/`; additional `skills/` roots may also be recognized.

```bash
python3 -m claudeclockwork.cli --skill-id manifest_registry_export --inputs "{}"
```

Useful entry points:

- `manifest_validate`
- `legacy_skill_inventory`
- `reference_skill_catalog`
- `plugin_scaffold`
- `plugin_registry_export`

Further notes: `Docs/full_skill_system_readme.md` and `Docs/skill_system_audit_and_roadmap.md`.
