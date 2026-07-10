# Design: Promote Skill-Forge Pipeline to First-Class LocalAI Runtime Capabilities

**Date:** 2026-03-16
**Status:** Ready for Implementation
**Scope:** Promote the forge pipeline from hidden/wrapper-script-only access into first-class runtime capabilities and a composed skill.

---

## Executive Summary

The skill-forge pipeline (code.plan, code.forge, code.review, code.validate) currently exists as a complete implementation but is only accessible through special wrapper scripts. This design promotes it into the normal LocalAI runtime and skill surface so it becomes a first-class capability accessible through standard `run_local_capability()` calls and a dedicated `skill_forge_run` composed skill.

**Target state:**
- `run_local_capability("code.plan", ...)` works natively
- `skill_forge_run(archetype, purpose, ...)` is the standard invocation for full pipelines
- Wrapper scripts remain as optional debug/convenience tools only
- Documentation reflects that LocalAI now supports code generation, not just embed/asr

---

## Architecture

### **Layer 1: Primitive First-Class Runtime Capabilities**

The four forge capabilities become first-class LocalAI runtime capabilities:
- `code.plan` - Convert forge_request to architecture plan
- `code.forge` - Generate code from plan
- `code.review` - Static analysis of generated code
- `code.validate` - Deterministic safety validation gates

**Implementation:**
- Create runner adapter classes:
  - `CodePlanRunner` wraps `CodePlanCapability.plan()`
  - `CodeForgeRunner` wraps `CodeForgeCapability.forge()`
  - `CodeReviewRunner` wraps `CodeReviewCapability.review()`
  - `CodeValidateRunner` wraps `CodeValidateCapability.validate()`
- Register all four in `claudeclockwork/localai/runtime.py` `_RUNNERS` dict
- Update `.claude/config/localai_registry.yaml` with all four capabilities
- Export runners from `claudeclockwork/localai/runners/__init__.py`

**Result:** `run_local_capability("code.plan", {...})` returns a contract-shaped result

---

### **Layer 2: Composed High-Level Skill**

Create a dedicated `skill_forge_run` skill that orchestrates the full pipeline.

**Location:** `.claude/skills/localai/skill_forge_run/`
- `manifest.json` - Skill metadata and contracts
- `skill.py` - `SkillForgeRun` orchestrator class

**Function Signature:**

```python
def skill_forge_run(
    archetype: str,
    purpose: str,
    allowed_write_roots: list[str] | None = None,
    target_root: str | None = None,
    report_file: str | None = None,
    mode: str = "full",
    publish: bool = True,
) -> dict[str, Any]:
    """
    Orchestrate the full skill-forge pipeline.

    Args:
        archetype: One of scanner, validator, reporter, transformer, registry_helper
        purpose: Human-readable task description
        allowed_write_roots: List of paths where code may write.
                           None → use policy-derived safe defaults
        target_root: Final destination for validated artifacts.
                    None → auto-generate in .claude/forge_outputs/<run_id>
        report_file: Where to write the run report.
                    None → auto-generate as report_file within target_root
        mode: Execution mode controlling which stages run.
              One of: "full", "plan_only", "through_forge",
                     "through_review", "validate_only"
              Default: "full"
        publish: If True, move validated artifacts to target_root after validation.
                Automatically skipped if mode stops before validation.
                Default: True

    Returns:
        Stage-structured result dict with run_id, all stage outputs, and final_status
    """
```

**Execution Lifecycle:**

```
prepare/scaffold
  ↓ (setup temp workspace, resolve inputs)
code.plan
  ↓ (via run_local_capability)
code.forge
  ↓ (via run_local_capability)
code.review
  ↓ (via run_local_capability)
code.validate
  ↓ (via run_local_capability)
publish/register
  ↓ (only if validation passed and publish=True)
[complete]
```

**Key principles:**
- Forge into temp workspace only
- Validate in temp workspace
- Only move to final target if validation passes
- Use `run_local_capability()` for all stages (no bypass paths)

---

## Partial Execution Modes

Each mode has explicit preconditions and guarantees:

### `mode="full"` (Default)

**Preconditions:** Base inputs only (archetype, purpose)
**Execution:** prepare → plan → forge → review → validate → publish
**Guarantees:**
- Temp workspace created and cleaned up per policy
- All stage results in output
- Artifacts moved to target_root if publish=True and validation passed
- Registry updated if register=True

### `mode="plan_only"`

**Preconditions:** Base inputs only
**Execution:** prepare → plan only
**Guarantees:**
- Plan result returned
- Publishing skipped automatically (no validated artifacts)
- Temp workspace returned for inspection

### `mode="through_forge"`

**Preconditions:** Base inputs only
**Execution:** prepare → plan → forge only
**Guarantees:**
- Plan and forge results returned
- Publishing skipped automatically (not reviewed/validated)
- Temp workspace returned for inspection

### `mode="through_review"`

**Preconditions:** Must have existing plan + forge outputs in temp workspace (requires either):
- Prior run_id with results in temp storage, OR
- Explicit paths to existing plan/forge results
**Execution:** Assume existing plan/forge → review only
**Guarantees:**
- Review result returned
- Publishing skipped automatically (not yet validated)
- Workspace preserved

### `mode="validate_only"`

**Preconditions:** Must have existing plan + forge + review outputs, OR explicit artifact path to validate
**Execution:** Load existing artifacts → validate only
**Guarantees:**
- Validation result returned
- Publishing skipped automatically (not a full run)
- Workspace preserved for inspection

---

## Publishing Behavior

**Publish vs. Register (Distinct Concepts):**
- **Publish:** Move validated artifacts from temp workspace to `target_root`
- **Register:** Update skill/capability registry if the artifact should become discoverable

**Publishing Logic:**
- If `mode="full"` and validation passes: publish artifacts to `target_root` (if `publish=True`)
- If `mode` is partial (anything else): publishing is skipped automatically, regardless of `publish=True`
- If `publish=True` with incompatible mode: return non-fatal note in result, do not error

**Registration Logic:**
- Only register if artifact is meant to become a reusable registered skill
- Not all forged outputs require registration (only specify if applicable to archetype)

---

## Return Structure

```python
{
    "run_id": "forge_20260316_143022_<archetype>",
    "resolved_inputs": {
        "archetype": "reporter",
        "purpose": "...",
        "allowed_write_roots": ["docs", "Docs"],
        "target_root": ".claude/forge_outputs/forge_20260316_143022_reporter",
        "report_file": ".claude/forge_outputs/forge_20260316_143022_reporter/run_report.json",
        "mode": "full",
        "publish": True,
    },
    "temp_workspace": "/tmp/forge_20260316_143022_reporter",
    "prepare_result": {
        "status": "ok",
        "temp_workspace": "/tmp/forge_20260316_143022_reporter",
        "resolved_write_roots": ["docs"],
    },
    "plan_result": {
        "status": "ok",
        "module_structure": {...},
        "key_functions": [...],
        "dependencies": [...]
    },
    "forge_result": {
        "status": "ok",
        "files_generated": {...},
        "package_root": "temp_workspace/generated"
    },
    "review_result": {
        "status": "ok",
        "issues": [],
        "suggestions": []
    },
    "validation_result": {
        "status": "ok",
        "gates_passed": ["syntax", "imports", "patterns", "roots", "schema", "smoke_test"]
    },
    "publish_result": {
        "status": "ok",
        "artifacts_moved": ["docs/FORGE_PIPELINE.md"],
        "registry_updated": False,
    },
    "final_status": "success",  # "success", "partial_success", "failed"
    "execution_log": [
        {
            "stage": "prepare",
            "status": "ok",
            "timestamp": "2026-03-16T14:30:22Z",
            "duration_ms": 145,
            "notes": "Resolved write_roots from policy"
        },
        {
            "stage": "plan",
            "status": "ok",
            "timestamp": "2026-03-16T14:30:23Z",
            "duration_ms": 892,
            "notes": None
        },
        ...
    ]
}
```

**Key details:**
- `execution_log` is a structured list of events, not a flat string
- Each event includes: stage, status, timestamp, duration, notes
- `temp_workspace` path is always returned (for inspection on failure)
- Partial modes set `final_status="partial_success"`

---

## Temp Workspace Management

**Lifecycle:**
1. Create temp workspace at start of `prepare` phase
2. All stages use this workspace
3. On failure: preserve workspace for debugging (return path in result)
4. On success: optionally clean up after publish + reporting (configurable)
5. Always return workspace path in result

**Cleanup Policy:**
- Never clean up on failure
- On success: offer cleanup as optional step (default: keep)
- Always return path so cleanup can be manual if desired

---

## Semantics: Target Root vs. Temp vs. Report

**Strict separation:**
- **Temp workspace:** `/tmp/forge_<run_id>` - Where forging happens; discarded after reporting
- **target_root:** User-specified or auto-generated final destination (e.g., `.claude/forge_outputs/<run_id>`) - Where validated artifacts live after publication
- **report_file:** Location of structured run report (e.g., `target_root/run_report.json`) - Metadata about the run itself

These three locations must remain logically distinct and clearly labeled in all output.

---

## Layer 3: Primitive Debug Access

No new files. Existing runners remain directly callable via `run_local_capability()` for development/debugging:

```python
# Direct primitive access for debugging
result = run_local_capability("code.plan", {...})
result = run_local_capability("code.forge", {...})
```

This is the appropriate path for pipeline developers and evaluation work.

---

## Layer 4: Discoverability & Documentation

**Files to create/update:**
- `.claude/config/localai_registry.yaml` - Add all four code.* capabilities
- `.claude/skills/localai/localai_run/manifest.json` - Update description to include code capabilities
- `.claude/policies/skill_autodiscovery_and_forge.md` - Clarify first-class status
- `.claude/agents/meta/skill_forge.md` - Update to reference new normal usage path
- `.claude/skills/localai/skill_forge_run/manifest.json` - New composed skill metadata

**Key outcome:** Documentation no longer claims LocalAI is "embed/asr only"

---

## Layer 5: Regression Coverage

**Test categories:**

1. **Unit tests for primitive runners:**
   - `tests/test_code_plan_runner.py`
   - `tests/test_code_forge_runner.py`
   - `tests/test_code_review_runner.py`
   - `tests/test_code_validate_runner.py`

2. **Runtime integration tests:**
   - `tests/test_runtime_forge_integration.py`
   - Verify `run_local_capability("code.plan", ...)` works
   - Same for forge, review, validate

3. **Composed skill tests:**
   - `tests/test_skill_forge_run_full_pipeline.py`
   - `tests/test_skill_forge_run_partial_modes.py`
   - `tests/test_skill_forge_run_validation_blocking.py`

4. **Regression proof:**
   - At least one test proving `run_local_capability("code.plan", ...)` does NOT return `unknown_capability`
   - Tests for all four capabilities
   - Tests for composed skill with various modes
   - Negative test: validation blocks invalid forge output

---

## Implementation Strategy: Incremental Decomposition

**Hard rule:** Implement one smallest verifiable unit at a time. Do not batch or defer verification.

**Phase 1: Primitive Capabilities (One at a Time)**

1. **1a.** Create `CodePlanRunner` adapter class
   - Wire into runtime
   - Update registry
   - Verify `run_local_capability("code.plan", ...)` works
   - Add unit + integration test
   - **Verify end-to-end before proceeding**

2. **1b.** Repeat for `CodeForgeRunner`, `CodeReviewRunner`, `CodeValidateRunner`
   - Same verification pattern for each
   - Implement one, verify, then next

**Phase 2: Composed Skill Shell**

3. **2a.** Create skill shell with input validation
   - Manifest + basic SkillForgeRun class
   - Validate archetype, purpose, inputs
   - Return basic success/error
   - Add shell test

4. **2b.** Wire prepared phase
   - Temp workspace creation
   - Input resolution (allowed_write_roots defaults)
   - Path generation (target_root, report_file)
   - Test temp workspace creation

5. **2c.** Wire orchestration (one stage at a time)
   - Add plan stage → call `run_local_capability("code.plan", ...)`
   - Test with actual plan runner
   - Repeat for forge, review, validate
   - **After each stage: verify integration before next**

6. **2d.** Wire publish/register logic
   - Move artifacts to target_root on success
   - Respect `publish` and `mode` flags
   - Test publish with various modes

7. **2e.** Structured logging
   - Build execution_log as list of events
   - Add timestamps, durations, stage transitions
   - Test log structure

**Phase 3: Documentation & Discovery**

8. **3a.** Update registry with four capabilities
9. **3b.** Update manifests and policy docs
10. **3c.** Verify discoverability

**Phase 4: Regression Coverage**

11. **4a.** Add unit tests for each runner
12. **4b.** Add integration tests for `run_local_capability()`
13. **4c.** Add composed skill tests
14. **4d.** Add negative tests (validation blocks invalid output)

---

## Error Recovery Strategy

**If implementation fails at any point:**

1. **Reduce scope:** Don't retry the full scope—isolate the failing component
2. **Complete smallest unit first:** Finish one runner, verify it, then next
3. **Method-by-method:** If a module is unstable, finish and verify it method-by-method
4. **Expand outward:** Only after smallest unit is verified, expand to next integration point

Example: If full runtime promotion fails, wire one capability first and verify `run_local_capability("code.plan", ...)` end-to-end before adding the other three.

---

## Acceptance Criteria

- [ ] A. `run_local_capability("code.plan", ...)` returns a contract-shaped result
- [ ] B. Same for `code.forge`, `code.review`, `code.validate`
- [ ] C. `localai_run` skill can invoke those capabilities
- [ ] D. A dedicated composed `skill_forge_run` exists
- [ ] E. Composed skill uses `run_local_capability()` for all orchestration
- [ ] F. No wrapper script required for normal Claude usage
- [ ] G. Docs and manifests updated; LocalAI no longer claimed as "embed/asr only"
- [ ] H. Regression tests prove integration
- [ ] I. Temp workspace lifecycle is correct: create, use, preserve on failure, clean up on success
- [ ] J. Partial modes work with explicit preconditions
- [ ] K. Publishing logic is mode-aware
- [ ] L. Execution log is structured (list of events, not flat string)

---

## Non-Goals

- Do not turn forge into an unrestricted code generator
- Do not weaken validation gates
- Do not create hidden bypass paths around `run_local_capability()`
- Do not treat partial execution as the normal mode
- Do not combine publish and register as a single operation

---

## References

- **Task:** `/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/Task.md`
- **Forge runtime:** `claudeclockwork/localai/runtime.py`
- **Registry:** `.claude/config/localai_registry.yaml`
- **Existing capabilities:** `claudeclockwork/localai/capabilities/`
- **Runner pattern:** `claudeclockwork/localai/runners/`
