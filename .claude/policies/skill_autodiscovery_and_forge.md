# Skill Autodiscovery and Forge Pipeline Policy

**Updated: 2026-03-16**
**Status: First-Class Runtime Capabilities**

## Overview

The skill-forge pipeline (code generation system) is now a **first-class LocalAI runtime capability**, fully integrated into the standard capability dispatch system alongside embed.text and audio.asr.

## Architecture

### Runtime Capabilities (First-Class)

The following are now standard LocalAI runtime capabilities accessible via `run_local_capability()`:

| Capability | Runner | Purpose |
|---|---|---|
| `embed.text` | EmbedRunner | Text vectorization and similarity search |
| `audio.asr` | AsrRunner | Audio transcription |
| `code.plan` | CodePlanRunner | Architecture planning from task descriptions |
| `code.forge` | CodeForgeRunner | Code generation from architecture plans |
| `code.review` | CodeReviewRunner | Static analysis of generated code |
| `code.validate` | CodeValidateRunner | Deterministic safety validation |

**All are directly accessible:**

```python
from claudeclockwork.localai import run_local_capability

# Primitive capability access (for debugging or pipeline composition)
plan = run_local_capability("code.plan", {
    "task_id": "test_001",
    "archetype": "reporter",
    "purpose": "Generate documentation",
    "constraints": {}
})

# Standard skill access
result = localai_run(capability="code.plan", inputs={...})
```

### Composed Skill: `skill_forge_run`

The dedicated composed skill orchestrates the full pipeline with multiple execution modes:

```python
from claudeclockwork.localai.skills.skill_forge_run import skill_forge_run

result = skill_forge_run(
    archetype="reporter",
    purpose="Generate comprehensive documentation",
    mode="full",  # or plan_only, through_forge, through_review, validate_only
    publish=True  # Move artifacts to target_root after validation
)
```

## Execution Modes

| Mode | Stages | Use Case |
|---|---|---|
| `full` | plan → forge → review → validate → publish | Complete pipeline; validation gates artifacts |
| `plan_only` | plan | Design phase; explore architecture |
| `through_forge` | plan → forge | Implementation preview; no review/validation |
| `through_review` | review | Analyze pre-generated code (requires prior plan+forge) |
| `validate_only` | validate | Safety gate check (requires prior plan+forge+review) |

## Preconditions

- **plan_only, through_forge**: No preconditions; start from scratch
- **through_review**: Requires prior `code.plan` and `code.forge` outputs
- **validate_only**: Requires prior outputs from all three stages (plan, forge, review)

## Publishing Behavior

- **Full mode + validation passed**: Artifacts move to `target_root`
- **Full mode + validation failed**: Artifacts remain in temp workspace
- **Partial modes**: Publishing is skipped regardless of `publish` parameter
- **Non-fatal**: Attempting `publish=True` with partial mode returns a note (not an error)

## Validation Gates

The `code.validate` capability enforces 6 deterministic gates (no LLM judgment):

1. **Syntax**: Generated code parses correctly
2. **Imports**: All imports are available/registered
3. **Patterns**: Code matches approved patterns (no malware signatures)
4. **Roots**: Code only writes to `allowed_write_roots`
5. **Schema**: Outputs match declared types/interfaces
6. **Smoke Test**: Code runs without exceptions in sandbox

## Archetype Constraints

The pipeline is constrained to **5 archetypes** (policy-enforced):

| Archetype | Purpose | Write Roots |
|---|---|---|
| `scanner` | Analyze code/files for metrics/patterns | readonly |
| `validator` | Validate data formats/schemas | readonly |
| `reporter` | Generate documentation/reports | docs, reports |
| `transformer` | Refactor/optimize code | src, generated |
| `registry_helper` | Generate registry entries | .claude/registry |

## Shell Wrappers (Deprecated)

Any existing shell launcher scripts (e.g., `run_forge_task.sh`) are **optional convenience tools only**. They are no longer the primary or required execution path.

**Standard usage path:** Use `skill_forge_run()` or `localai_run(capability="code.*", ...)` directly.

## Discoverability

All four code.* capabilities are:
- ✅ Registered in `.claude/config/localai_registry.yaml`
- ✅ Exported from `claudeclockwork/localai/runners/__init__.py`
- ✅ Wired into `claudeclockwork/localai/runtime.py` `_RUNNERS` dict
- ✅ Documented in `localai_run` skill manifest
- ✅ Available via `run_local_capability()` calls

## Testing & Verification

All capabilities are covered by:
- Unit tests for each runner (test_code_*_runner.py)
- Integration tests for `run_local_capability()` (test_runtime_forge_integration.py)
- Composed skill tests for all modes and preconditions (test_skill_forge_run.py)
- Regression test: Calling `run_local_capability("code.plan", ...)` no longer returns `unknown_capability`

## Future Enhancements

Potential future capabilities:
- `code.refactor`: AST-based code transformation
- `code.optimize`: Performance analysis and optimization suggestions
- `code.document`: Automatic docstring generation
- `code.test`: Unit test generation from code patterns

All follow the same pattern: BaseRunner adapter → runtime registration → registry entry.

---

**Related files:**
- `claudeclockwork/localai/runtime.py` — Runtime dispatch
- `claudeclockwork/localai/runners/*.py` — Capability implementations
- `.claude/config/localai_registry.yaml` — Capability registry
- `claudeclockwork/localai/skills/skill_forge_run.py` — Composed orchestrator
- `.claude/skills/localai/skill_forge_run/manifest.json` — Skill metadata
