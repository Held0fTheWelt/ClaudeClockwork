# Skill-Forge Pipeline Integration Guide

**For developers integrating the forge pipeline into applications.**

## Quick Start

### Invoke Full Pipeline

```python
from claudeclockwork.localai.skills.skill_forge_run import skill_forge_run

result = skill_forge_run(
    archetype="reporter",
    purpose="Generate API documentation from OpenAPI spec",
    allowed_write_roots=["docs"],
    publish=True
)

assert result["final_status"] == "success"
print(f"Generated: {result['resolved_inputs']['report_file']}")
```

### Invoke Individual Capabilities

```python
from claudeclockwork.localai import run_local_capability

# Use via the generic localai_run skill
result = localai_run(
    capability="code.plan",
    inputs={
        "task_id": "my_task",
        "archetype": "reporter",
        "purpose": "Generate docs",
        "constraints": {}
    }
)

assert result["status"] == "ok"
```

## Testing

### Unit Tests

```bash
# Test each runner individually
pytest tests/test_code_plan_runner.py -v
pytest tests/test_code_forge_runner.py -v
pytest tests/test_code_review_runner.py -v
pytest tests/test_code_validate_runner.py -v
```

### Integration Tests

```bash
# Test runtime dispatch
pytest tests/test_runtime_forge_integration.py -v

# Test composed skill with all modes
pytest tests/test_skill_forge_run.py -v
```

### Regression Tests

```bash
# Verify run_local_capability no longer returns unknown_capability
pytest tests/test_forge_regression.py -v
```

## Error Handling

```python
result = skill_forge_run(archetype="reporter", purpose="Test")

# Check status
if result["final_status"] == "success":
    handle_success(result)
elif result["final_status"] == "partial_success":
    handle_partial(result)  # Partial mode or non-fatal issue
else:  # "failed"
    handle_failure(result)  # Precondition or stage failure

# Inspect individual stage results
for stage in ["plan", "forge", "review", "validation"]:
    stage_key = f"{stage}_result"
    if result[stage_key] and result[stage_key].get("status") == "error":
        print(f"{stage} failed: {result[stage_key].get('error')}")

# View full execution history
for event in result["execution_log"]:
    if event["status"] == "error":
        print(f"[{event['stage']}] {event['notes']} ({event['duration_ms']}ms)")
```

## Publishing Behavior

### Full Mode (Default)

```python
result = skill_forge_run(
    archetype="reporter",
    purpose="Generate docs",
    target_root=".claude/forge_outputs/my_docs",
    publish=True
)

# If validation passes, artifacts are in .claude/forge_outputs/my_docs/
# If validation fails, artifacts remain in /tmp/forge_xxx/ for inspection
```

### Partial Modes

```python
result = skill_forge_run(
    archetype="reporter",
    purpose="Test plan generation",
    mode="plan_only",
    publish=True
)

# Even with publish=True, partial modes skip publishing
# Inspect result["plan_result"] directly
```

## Mode Selection

- **mode="full"**: Default; complete pipeline with validation gates
- **mode="plan_only"**: Architecture only; no code generation
- **mode="through_forge"**: Plan + generation; skip review/validation for speed
- **mode="through_review"**: Analyze pre-generated code (requires prior outputs)
- **mode="validate_only"**: Safety check only (requires prior outputs)

## Workspace Management

### Default Behavior

- Temp workspace created at `/tmp/forge_<run_id>/`
- On failure: workspace preserved for debugging; path returned in result
- On success: workspace may be cleaned up per policy

### Custom Workspace

```python
result = skill_forge_run(
    archetype="reporter",
    purpose="Generate docs",
    target_root="/custom/path/to/outputs",
    report_file="/custom/path/to/outputs/report.json"
)

# Report will be written to specified location
```

## Monitoring & Logging

### Execution Log

Each result includes structured `execution_log`:

```python
for event in result["execution_log"]:
    print(f"{event['stage']:15} {event['status']:10} "
          f"{event['duration_ms']:5}ms - {event['notes']}")

# Output:
# validate_inputs  ok         10ms - Validated archetype='reporter', mode='full'
# input_resolution ok         15ms - Resolved inputs and defaults for mode='full'
# plan             ok         892ms - Invoked code.plan
# ...
```

### Cost Tracking

All stages use `run_local_capability()`, which respects cost tracking:

```python
result = skill_forge_run(...)

# Cost per stage available in individual stage results
for stage_key in ["plan_result", "forge_result", "review_result", "validation_result"]:
    if result[stage_key]:
        print(f"{stage_key}: {result[stage_key].get('metrics', {})}")
```

## Debugging

### Inspect Temp Workspace

```python
result = skill_forge_run(...)
temp = result["temp_workspace"]

# Manually inspect generated files
import os
for root, dirs, files in os.walk(temp):
    for file in files:
        print(os.path.join(root, file))
```

### Step-by-Step Execution

Use primitive capabilities instead of composed skill:

```python
# Step 1
plan = run_local_capability("code.plan", {...})
assert plan["status"] == "ok"

# Step 2
forge = run_local_capability("code.forge", {"plan": plan["outputs"]})
# If forge fails, you know exactly where
```

---

**See also:**
- `.claude/policies/skill_autodiscovery_and_forge.md` — Policies and constraints
- `.claude/agents/meta/skill_forge.md` — Agent usage examples
