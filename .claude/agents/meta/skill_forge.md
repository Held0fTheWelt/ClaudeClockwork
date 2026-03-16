# Skill-Forge Agent Guide

**Updated: 2026-03-16**

## Invocation

The skill-forge pipeline is now directly accessible as a first-class skill and runtime capability.

### Standard Usage (Recommended)

Use the dedicated composed skill:

```python
# In a skill or agent script
from claudeclockwork.localai.skills.skill_forge_run import skill_forge_run

result = skill_forge_run(
    archetype="reporter",
    purpose="Generate comprehensive API documentation from code",
    allowed_write_roots=["docs"],
    target_root=".claude/forge_outputs/api_docs",
    mode="full",
    publish=True
)

if result["final_status"] == "success":
    print(f"Documentation generated: {result['target_root']}")
else:
    print(f"Generation failed: {result['errors']}")
```

### Primitive Capability Access (Debugging)

For pipeline composition or step-by-step execution:

```python
from claudeclockwork.localai import run_local_capability

# Step 1: Generate plan
plan = run_local_capability("code.plan", {
    "task_id": "task_001",
    "archetype": "reporter",
    "purpose": "Generate documentation",
    "constraints": {}
})

# Step 2: Generate code from plan
forge = run_local_capability("code.forge", {
    "task_id": "task_001",
    "plan": plan["outputs"],
    "allowed_write_roots": ["docs"]
})

# Step 3: Review generated code
review = run_local_capability("code.review", {
    "task_id": "task_001",
    "forge_output": forge["outputs"]
})

# Step 4: Validate
validate = run_local_capability("code.validate", {
    "task_id": "task_001",
    "forge_output": forge["outputs"]
})
```

## Execution Modes

### Full Pipeline (Default)

```python
skill_forge_run(
    archetype="transformer",
    purpose="Refactor authentication module",
    mode="full"
)
```

Executes: plan → forge → review → validate → publish

### Plan Only

```python
result = skill_forge_run(
    archetype="reporter",
    purpose="Explore how to document this API",
    mode="plan_only"
)

# result["plan_result"] contains the architecture plan
# No code is generated; just planning
```

### Through Forge

```python
result = skill_forge_run(
    archetype="validator",
    purpose="Generate data validation schema",
    mode="through_forge"
)

# result["plan_result"] and result["forge_result"] are available
# No review/validation; inspect the generated code manually
```

## Archetype Selection

| Archetype | When to Use |
|---|---|
| `scanner` | Generate code analysis tools, metrics reporters, pattern detectors |
| `validator` | Generate schema validators, format checkers, data validators |
| `reporter` | Generate documentation, reports, summaries, examples |
| `transformer` | Generate code refactoring, optimization, migration scripts |
| `registry_helper` | Generate skill manifests, config entries, registry updates |

## Result Structure

```python
{
    "run_id": "forge_20260316_143022_reporter",
    "resolved_inputs": {
        "archetype": "reporter",
        "purpose": "...",
        "allowed_write_roots": ["docs"],
        "target_root": ".claude/forge_outputs/forge_20260316_143022_reporter",
        "mode": "full",
        "publish": true
    },
    "temp_workspace": "/tmp/forge_20260316_143022_reporter",
    "plan_result": {...},  # Code.plan output
    "forge_result": {...},  # Code.forge output
    "review_result": {...},  # Code.review output
    "validation_result": {...},  # Code.validate output (if reached)
    "publish_result": {...},  # Artifact publishing info (if reached)
    "final_status": "success" | "partial_success" | "failed",
    "execution_log": [
        {
            "stage": "plan",
            "status": "ok",
            "timestamp": "2026-03-16T14:30:23Z",
            "duration_ms": 892,
            "notes": "Invoked code.plan"
        },
        ...
    ]
}
```

## Validation Gates

The `code.validate` stage enforces 6 safety gates:

1. **Syntax** — Generated code must parse correctly
2. **Imports** — All imports must be available
3. **Patterns** — Code must match approved patterns (blocks malware signatures)
4. **Roots** — Code may only write to `allowed_write_roots`
5. **Schema** — Outputs must match declared types
6. **Smoke Test** — Code must run in sandbox without exceptions

If any gate fails, the validation result is marked as failed and artifacts are not published.

## Error Handling

Check `final_status` field:

- `"success"` — All stages completed, artifacts published
- `"partial_success"` — Partial mode completed or full mode hit a non-fatal issue
- `"failed"` — Required preconditions not met or a stage failed

For failure details:

```python
if result["final_status"] == "failed":
    for entry in result["execution_log"]:
        if entry["status"] == "error":
            print(f"Stage {entry['stage']}: {entry['notes']}")
```

## Performance Notes

- **Planning stage** typically takes 2-5s (small LLM call)
- **Code generation** typically takes 10-30s depending on complexity
- **Validation** is deterministic: <1s per gate

Total time for full pipeline: 15-40s for typical tasks.

## Historical Note

Prior to March 2026, the forge pipeline was accessible only through special wrapper scripts. As of March 2026, it is a **first-class runtime capability** with standard skill and capability interfaces. Wrapper scripts remain as optional convenience tools but are no longer the required access path.
