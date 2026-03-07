# Architecture Overview (Stub)

> This is a stub. For the full system architecture see the root `ARCHITECTURE.md`.

## Primary Package: `claudeclockwork/`

The canonical Python package is `claudeclockwork/`. It is the execution runtime for the Clockwork governance layer.

## CLI Entry Point

```bash
python -m claudeclockwork.cli --skill-id <skill_name> --inputs '{...}'
python -m claudeclockwork.mcp   # MCP STDIO server (optional)
```

## Key Modules

| Module | Purpose |
|--------|---------|
| `claudeclockwork/cli.py` | CLI entry point — argument parsing, skill dispatch, plugin healthcheck |
| `claudeclockwork/runtime.py` | Runtime bootstrap — builds registry, executor, planner, loads permissions |
| `claudeclockwork/bridge.py` | Manifest bridge — `run_manifest_skill()`, `LegacySkillAdapter` |
| `claudeclockwork/mcp/` | Optional MCP STDIO server — exposes skills as MCP tools and resources |
| `claudeclockwork/core/registry/` | Skill discovery — walks `.claude/skills/*/manifest.json` |
| `claudeclockwork/core/executor/` | Execution pipeline — `SkillExecutor`, `ExecutionPipeline` |
| `claudeclockwork/core/planner/` | Planning and routing logic |
| `claudeclockwork/core/security/` | `PermissionManager` — permission allow/block enforcement |
| `claudeclockwork/core/models/` | Data models — `ExecutionContext`, `SkillResult`, `SkillManifest` |
| `claudeclockwork/core/plugin/` | Plugin loader, registry, and dependency resolver |

## Governance Layer: `.claude/`

The `.claude/` directory is the governance layer — agent definitions, skill manifests, config, contracts, and knowledge base. It is portable and can be deployed independently of this repository. See `.claude/DEPLOY.md`.

## Two Dispatch Paths

| Path | Entry point | Skills |
|------|-------------|--------|
| Manifest CLI | `python -m claudeclockwork.cli` | 97 manifest skills |
| Legacy runner | `python3 .claude/tools/skills/skill_runner.py` | 97 skills (same set, all reachable) |

> For full detail on the dispatch architecture see `CLAUDE.md` — "Skill Dispatch: Two Parallel Systems".
