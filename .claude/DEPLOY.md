# Clockwork Deployment Guide

This document is the authoritative reference for deploying Clockwork into a consuming project.

---

## Deployable Unit

The entire `.claude/` directory is the Clockwork plugin. Copy it to the root of the consuming project:

```bash
cp -r /path/to/ClaudeClockwork/.claude /path/to/your-project/.claude
```

Then install the runtime package:

```bash
pip install claudeclockwork
# or for a local/editable install:
pip install -e /path/to/ClaudeClockwork
```

That is the complete deployment. No other files from this repository are required.

---

## Post-Copy Setup

1. **Update `.claude/VERSION`** — record the Clockwork version being deployed (e.g. `18.1.0`).

2. **Create `.project/` structure** for the consuming project:
   ```
   .project/
     MEMORY.md               # Cross-session knowledge (copy from Clockwork repo as template)
     ARCHITECTURE.md         # System design for your project
     ROADMAP.md              # Active milestones for your project
     MODEL_POLICY.md         # Model tier overrides (leave empty if using defaults)
     QUALITY_TRACKING.md     # Telemetry + stats
     memory/                 # Team Lead cross-session context files
     Docs/
       Plans/
       Review/
       Critics/
       Documentation/
       References/
       Tutorials/
   ```

3. **Create a project-specific `CLAUDE.md`** at the consuming project root. Do not copy Clockwork's `CLAUDE.md` verbatim — it is specific to Clockwork development. Use it as a structural template.

4. **Review `.claude/config/permissions.json`** — adjust the allowed/blocked permission sets to match the consuming project's security profile.

5. **Run boot check** to verify the environment:
   ```bash
   python3 .claude/tools/boot_check.py
   ```

---

## What NOT to Copy

The following directories and files exist only for Clockwork development and must **not** be copied to consuming projects:

| Path | Reason |
|------|--------|
| `mvps/` | Clockwork internal MVP plans |
| `roadmaps/` | Clockwork internal roadmaps |
| `.claude-development/` | Legacy development archive (pre-v18) |
| `Docs/` | Legacy skill audit artifacts |
| `tests/` | Clockwork test suite — not meaningful in other projects |
| `scripts/` | Clockwork dev/generation scripts |
| `validation_runs/` | Local validation output (transient) |
| `validation_runs_redacted/` | Redacted validation output (transient) |
| `memory/` | Dev session memory (project-specific) |
| `claudeclockwork/` | Install via pip — do not copy raw source |
| `CLAUDE.md` | Replace with a project-specific version |
| `NEW_MVPS.md` | Clockwork planning artifact |
| `VERIFY.md` | Clockwork audit output |

---

## Architecture: Two Distinct Layers

```
.claude/              ← Governance layer (copy this)
  agents/             Agent role definitions
  config/             Runtime config (permissions, pricing, routing)
  contracts/          JSON schemas for inter-agent data
  governance/         Execution protocol, policies
  skills/             Manifest skill packages
  tools/              Deterministic Python tools + legacy skill scripts
  knowledge/          Librarian-managed knowledge base

claudeclockwork/      ← Runtime layer (install via pip)
  cli.py              CLI entry point
  runtime.py          Registry + executor builder
  bridge.py           Manifest skill dispatcher
  mcp/                Optional MCP STDIO server
  core/               Executor, planner, registry, security, models
```

These are intentionally separate:
- `.claude/` is portable governance — it travels with the project.
- `claudeclockwork/` is the execution engine — it is installed as a versioned Python package dependency.

---

## Minimum Python Version

Python 3.10+. No mandatory external dependencies beyond the standard library for core operation. Optional dependencies:
- `mcp` — required only for `python3 -m claudeclockwork.mcp` (STDIO server)
- `jsonschema` — used by manifest validation gate
- `pytest` — required only for running the Clockwork test suite
