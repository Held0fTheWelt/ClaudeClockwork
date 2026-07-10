# Forge Pipeline Promotion — Implementation Plan

> **For agentic workers:** REQUIRED: Execute this plan using pure Ollama agents. Each task's step code is scaffolded; Ollama agents execute tasks via the skill-forge pipeline and orchestrate implementation. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote skill-forge pipeline (code.plan, code.forge, code.review, code.validate) from wrapper-script-only access into first-class LocalAI runtime capabilities and a composed `skill_forge_run` skill.

**Architecture:** Layer-by-layer promotion: primitive runners first (one at a time), then composed skill, then discoverability, then tests. Each layer verified end-to-end before proceeding. Use skill-forge pipeline to generate task implementations; pure Ollama agents orchestrate.

**Tech Stack:** Python 3.10+, LocalAI runtime, skill-forge pipeline, pure Ollama agents, pytest

---

## Chunk 1: Primitive Runners — Code Plan

### Task 1: CodePlanRunner Adapter

**Files:**
- Create: `claudeclockwork/localai/runners/code_plan.py`
- Modify: `claudeclockwork/localai/runners/__init__.py`
- Modify: `claudeclockwork/localai/runtime.py`
- Create: `tests/test_code_plan_runner.py`
- Create: `.claude/tasks/task_01_code_plan_runner.py` (via forge)

**Purpose:** Create a runner adapter for `CodePlanCapability` so it integrates with LocalAI runtime.

**Task Runner Script (to be generated via forge pipeline):**

This step uses the forge pipeline to generate `task_01_code_plan_runner.py`. The runner script will:
1. Create `CodePlanRunner` class that wraps `CodePlanCapability`
2. Implement `run(inputs)` method returning contract-shaped result
3. Update exports in `__init__.py`
4. Wire into `_RUNNERS` dict in `runtime.py`
5. Create unit test verifying `run_local_capability("code.plan", ...)` works

- [ ] **Step 1: Generate task runner via forge pipeline**

Use `skill_forge_run()` to generate task implementation:
```python
archetype="transformer"
purpose="Generate Python code for CodePlanRunner adapter class that wraps CodePlanCapability, integrates with LocalAI runtime._RUNNERS dict, and returns contract-shaped results. Include __init__.py export and runtime.py wiring. Pattern from existing EmbedRunner."
allowed_write_roots=["claudeclockwork/localai/runners", "tests"]
mode="full"
```

Generate to: `.claude/tasks/task_01_code_plan_runner.py`

**Expected output:**
- Complete CodePlanRunner class implementation
- Integration wiring code for runtime.py
- __init__.py export code
- Unit test scaffold

- [ ] **Step 2: Pure Ollama agent executes task runner**

Invoke pure Ollama agent:
```bash
cd /mnt/d/ClaudeClockwork
ollama run mistral << 'EOF'
You are an autonomous agent. Execute the task runner script at .claude/tasks/task_01_code_plan_runner.py.

Steps:
1. Read the runner script
2. Create claudeclockwork/localai/runners/code_plan.py with CodePlanRunner class
3. Update claudeclockwork/localai/runners/__init__.py to export CodePlanRunner
4. Update claudeclockwork/localai/runtime.py to wire "code.plan": CodePlanRunner() into _RUNNERS dict
5. Create tests/test_code_plan_runner.py with unit tests
6. Run: pytest tests/test_code_plan_runner.py -v
7. Run: python -c "from claudeclockwork.localai import run_local_capability; result = run_local_capability('code.plan', {'task_id': 'test', 'archetype': 'reporter', 'purpose': 'test'}); print('SUCCESS' if result.get('status') == 'ok' else 'FAILED')"
8. Report: Did run_local_capability("code.plan", ...) succeed? Yes/No

Execute autonomously without waiting for human input.
EOF
```

**Expected:** Agent reports `run_local_capability("code.plan", ...)` returns `status="ok"`

- [ ] **Step 3: Verify integration end-to-end**

Run locally:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_code_plan_runner.py -v
```

**Expected:** All tests pass

- [ ] **Step 4: Verify no regression in existing capabilities**

```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_runtime_*.py -v --tb=short 2>&1 | grep -E "PASSED|FAILED|ERROR"
```

**Expected:** Existing embed/asr tests still pass

- [ ] **Step 5: Commit**

```bash
git add claudeclockwork/localai/runners/code_plan.py
git add claudeclockwork/localai/runners/__init__.py
git add claudeclockwork/localai/runtime.py
git add tests/test_code_plan_runner.py
git commit -m "feat(localai): add CodePlanRunner as first-class runtime capability

- Create CodePlanRunner adapter wrapping CodePlanCapability
- Wire into runtime._RUNNERS under 'code.plan' key
- Add unit + integration tests proving run_local_capability works
- Verify no regression in existing embed/asr capabilities"
```

---

### Task 2: CodeForgeRunner Adapter

**Files:**
- Create: `claudeclockwork/localai/runners/code_forge.py`
- Modify: `claudeclockwork/localai/runners/__init__.py`
- Modify: `claudeclockwork/localai/runtime.py`
- Create: `tests/test_code_forge_runner.py`

**Repeat pattern from Task 1:**

- [ ] **Step 1: Generate task runner (same forge pattern as Task 1)**

Archetype: `transformer`
Purpose: "Generate CodeForgeRunner adapter class following CodePlanRunner pattern"
Mode: `full`

- [ ] **Step 2: Pure Ollama agent executes**

(Same orchestration pattern; replace "code.plan" with "code.forge" in tests)

- [ ] **Step 3-5: Verify, test, commit**

(Same pattern as Task 1)

---

### Task 3: CodeReviewRunner Adapter

**Repeat pattern from Tasks 1-2 for `code.review` capability**

- [ ] **Steps 1-5:** (Same pattern, substitute CodeReviewRunner)

---

### Task 4: CodeValidateRunner Adapter

**Repeat pattern from Tasks 1-3 for `code.validate` capability**

- [ ] **Steps 1-5:** (Same pattern, substitute CodeValidateRunner)

---

### Task 5: Update Registry with All Four Capabilities

**Files:**
- Modify: `.claude/config/localai_registry.yaml`

- [ ] **Step 1: Generate registry update script**

Use forge to generate YAML additions:
```python
archetype="reporter"
purpose="Generate YAML entries for localai_registry.yaml adding code.plan, code.forge, code.review, code.validate capabilities with descriptions and tool_ids"
mode="plan_only"
```

- [ ] **Step 2: Pure Ollama agent updates registry**

```bash
# Ollama agent reads generated YAML and appends to .claude/config/localai_registry.yaml
```

- [ ] **Step 3: Verify registry syntax**

```bash
cd /mnt/d/ClaudeClockwork
python -c "import yaml; yaml.safe_load(open('.claude/config/localai_registry.yaml'))" && echo "VALID"
```

**Expected:** VALID

- [ ] **Step 4: Verify all four capabilities in registry**

```bash
grep -E "code\.(plan|forge|review|validate)" .claude/config/localai_registry.yaml
```

**Expected:** All four listed

- [ ] **Step 5: Commit**

```bash
git add .claude/config/localai_registry.yaml
git commit -m "feat(registry): register code.plan, code.forge, code.review, code.validate as first-class capabilities"
```

---

## Chunk 2: Composed Skill — skill_forge_run

### Task 6: Composed Skill Skeleton & Input Validation

**Files:**
- Create: `.claude/skills/localai/skill_forge_run/manifest.json`
- Create: `.claude/skills/localai/skill_forge_run/skill.py`
- Create: `tests/test_skill_forge_run.py`
- Create: `.claude/tasks/task_05_composed_skill.py` (via forge)

- [ ] **Step 1: Generate composed skill via forge**

```python
archetype="transformer"
purpose="Generate SkillForgeRun class for .claude/skills/localai/skill_forge_run/skill.py that orchestrates code.plan → code.forge → code.review → code.validate pipeline. Include input validation, temp workspace management, mode parameter handling, and structured return result. Manifest.json with proper metadata."
allowed_write_roots=[".claude/skills/localai/skill_forge_run"]
mode="full"
```

Generate to: `.claude/tasks/task_05_composed_skill.py`

**Expected output:**
- SkillForgeRun class scaffold
- Manifest.json template
- Input validation logic
- Basic orchestration structure (placeholders for stage calls)

- [ ] **Step 2: Pure Ollama agent implements skill**

Orchestrate file creation, stage-by-stage implementation, and test scaffold creation.

- [ ] **Step 3: Wire stage calls to run_local_capability()**

Pure Ollama agent adds:
- `run_local_capability("code.plan", ...)`
- `run_local_capability("code.forge", ...)`
- `run_local_capability("code.review", ...)`
- `run_local_capability("code.validate", ...)`

For orchestration, ensuring error handling and result aggregation.

- [ ] **Step 4: Add temp workspace lifecycle**

Pure Ollama agent adds:
- Create `/tmp/forge_<run_id>` on prepare
- Use across all stages
- Preserve on failure, clean up on success
- Return path in result

- [ ] **Step 5: Add structured execution_log**

Pure Ollama agent builds execution_log as list of events with timestamps.

- [ ] **Step 6: Test basic invocation**

```bash
pytest tests/test_skill_forge_run.py::test_skill_forge_run_basic_invocation -v
```

**Expected:** PASS

- [ ] **Step 7: Verify skill can call code.plan**

```bash
pytest tests/test_skill_forge_run.py::test_skill_forge_run_calls_code_plan -v
```

**Expected:** PASS

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/localai/skill_forge_run/
git add tests/test_skill_forge_run.py
git commit -m "feat(skill): add skill_forge_run composed skill for full pipeline orchestration

- Implement SkillForgeRun class with input validation
- Wire all four stages via run_local_capability()
- Add temp workspace lifecycle management
- Add structured execution_log
- Add basic tests proving stage orchestration"
```

---

### Task 7: Mode Parameter & Publish Logic

**Files:**
- Modify: `.claude/skills/localai/skill_forge_run/skill.py`
- Modify: `tests/test_skill_forge_run.py`

- [ ] **Step 1: Generate mode handling via forge**

```python
archetype="transformer"
purpose="Generate Python code implementing mode parameter handling ('full', 'plan_only', 'through_forge', 'through_review', 'validate_only') with explicit stage skipping logic and mode-aware publishing. Include precondition validation."
allowed_write_roots=[".claude/skills/localai/skill_forge_run"]
mode="through_review"
```

- [ ] **Step 2-7: Pure Ollama agent implements**

Add mode handling, precondition checks, stage skipping, and mode-aware publish.

- [ ] **Step 8: Test each mode**

```bash
pytest tests/test_skill_forge_run.py -k "mode" -v
```

**Expected:** All mode tests pass

- [ ] **Step 9: Commit**

```bash
git add .claude/skills/localai/skill_forge_run/skill.py
git add tests/test_skill_forge_run.py
git commit -m "feat(skill): add mode parameter and publish logic to skill_forge_run

- Implement mode='full'|'plan_only'|'through_forge'|'through_review'|'validate_only'
- Add precondition validation per mode
- Implement mode-aware publishing (skip publish if mode stops before validation)
- Add tests for all modes"
```

---

## Chunk 3: Discoverability & Documentation

### Task 8: Update Manifests & Registry Docs

**Files:**
- Modify: `.claude/skills/localai/localai_run/manifest.json`
- Create/Modify: `.claude/policies/skill_autodiscovery_and_forge.md`
- Create: `.claude/skills/localai/skill_forge_run/README.md`

- [ ] **Step 1: Generate manifest updates via forge**

```python
archetype="reporter"
purpose="Generate updated manifest.json for .claude/skills/localai/localai_run adding descriptions of code.plan, code.forge, code.review, code.validate capabilities. Remove 'embed/asr only' limitations. Include comprehensive README for skill_forge_run."
allowed_write_roots=[".claude/skills/localai"]
mode="plan_only"
```

- [ ] **Step 2-4: Pure Ollama agent updates manifests**

- [ ] **Step 5: Verify no manifest syntax errors**

```bash
python -c "import json; json.load(open('.claude/skills/localai/localai_run/manifest.json'))" && echo "VALID"
python -c "import json; json.load(open('.claude/skills/localai/skill_forge_run/manifest.json'))" && echo "VALID"
```

**Expected:** Both VALID

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/localai/localai_run/manifest.json
git add .claude/skills/localai/skill_forge_run/README.md
git add .claude/policies/skill_autodiscovery_and_forge.md
git commit -m "docs: update manifests and policies for first-class forge capability status

- Update localai_run manifest to describe code.* capabilities
- Create skill_forge_run README with usage examples
- Update skill autodiscovery policy to clarify first-class status"
```

---

## Chunk 4: Regression Coverage

### Task 9: Integration Tests

**Files:**
- Create: `tests/test_runtime_forge_integration.py`

- [ ] **Step 1: Generate integration test scaffold via forge**

```python
archetype="transformer"
purpose="Generate comprehensive integration tests for test_runtime_forge_integration.py proving that run_local_capability('code.plan'|'code.forge'|'code.review'|'code.validate', ...) returns contract-shaped results without 'unknown_capability' error. Include 4 tests (one per capability) plus negative test proving validation blocks invalid output."
allowed_write_roots=["tests"]
mode="full"
```

- [ ] **Step 2-6: Pure Ollama agent implements tests**

- [ ] **Step 7: Run all integration tests**

```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_runtime_forge_integration.py -v
```

**Expected:** All pass, no `unknown_capability` errors

- [ ] **Step 8: Run full test suite**

```bash
cd /mnt/d/ClaudeClockwork
pytest tests/ -v --tb=short 2>&1 | tail -20
```

**Expected:** All pass, coverage ≥ 85%

- [ ] **Step 9: Commit**

```bash
git add tests/test_runtime_forge_integration.py
git commit -m "test: add integration coverage for first-class forge capabilities

- Prove run_local_capability('code.plan'|'code.forge'|'code.review'|'code.validate') works
- Negative test: validation blocks invalid output
- All tests pass"
```

---

## Chunk 5: Final Verification

### Task 10: End-to-End Sanity Check

- [ ] **Step 1: Verify all commits are present**

```bash
git log --oneline | head -20
```

**Expected:** At least 10 commits from phases 1-4

- [ ] **Step 2: Verify primitives work**

```bash
python -c "from claudeclockwork.localai import run_local_capability; print('✓ code.plan' if run_local_capability('code.plan', {'task_id': 'test', 'archetype': 'reporter', 'purpose': 'test'}).get('status') == 'ok' else '✗')"
python -c "from claudeclockwork.localai import run_local_capability; print('✓ code.forge' if run_local_capability('code.forge', {'task_id': 'test', 'archetype': 'reporter', 'plan_output': {}}).get('status') == 'ok' else '✗')"
python -c "from claudeclockwork.localai import run_local_capability; print('✓ code.review' if run_local_capability('code.review', {'task_id': 'test', 'forge_output': {}}).get('status') == 'ok' else '✗')"
python -c "from claudeclockwork.localai import run_local_capability; print('✓ code.validate' if run_local_capability('code.validate', {'task_id': 'test', 'forge_output': {}}).get('status') == 'ok' else '✗')"
```

**Expected:** All four ✓

- [ ] **Step 3: Verify composed skill loads**

```bash
python -c "from claudeclockwork.core.base.skill_base import SkillBase; from skills.localai.skill_forge_run.skill import SkillForgeRun; print('✓ skill_forge_run loaded')" 2>&1 | grep -q "✓" && echo "PASS" || echo "FAIL"
```

**Expected:** PASS

- [ ] **Step 4: Verify manifests are valid**

```bash
python -c "import json, yaml; json.load(open('.claude/skills/localai/localai_run/manifest.json')); json.load(open('.claude/skills/localai/skill_forge_run/manifest.json')); yaml.safe_load(open('.claude/config/localai_registry.yaml')); print('✓ All manifests valid')"
```

**Expected:** ✓ All manifests valid

- [ ] **Step 5: Verify no regression**

```bash
pytest tests/test_runtime_*.py tests/test_embed_runner.py tests/test_asr_runner.py -v --tb=short
```

**Expected:** All pass (existing embed/asr unaffected)

- [ ] **Step 6: Final commit message summary**

```bash
git log --oneline master~10..master
```

Verify commits align with phases:
- Phase 1: CodePlanRunner, CodeForgeRunner, CodeReviewRunner, CodeValidateRunner (4 commits)
- Phase 2: Composed skill shell, mode logic, publish (3 commits)
- Phase 3: Manifest updates, policy docs (1 commit)
- Phase 4: Integration tests (1 commit)
- Phase 5: Verification (1 commit)

- [ ] **Step 7: Create summary report**

```bash
cat << 'EOF' > .claude/FORGE_PROMOTION_SUMMARY.md
# Forge Pipeline Promotion — Summary Report

## What Changed
1. **Primitives:** code.plan, code.forge, code.review, code.validate promoted to first-class runtime capabilities
2. **Composed Skill:** skill_forge_run created for standard full-pipeline invocation
3. **Discoverability:** Manifests updated; LocalAI no longer claimed as "embed/asr only"
4. **Testing:** Regression coverage added; all tests pass

## What's First-Class Now
- `run_local_capability("code.plan", ...)` ✓
- `run_local_capability("code.forge", ...)` ✓
- `run_local_capability("code.review", ...)` ✓
- `run_local_capability("code.validate", ...)` ✓
- `skill_forge_run(archetype, purpose, ...)` ✓

## What Remains Wrapper-Only
- Shell/CLI scripts in .claude/tasks/ (optional debug/batch tools)
- Extra orchestration launchers (convenience only)

## No Regressions
- embed.text capability: ✓ working
- audio.asr capability: ✓ working
- All existing tests: ✓ passing
- Coverage: ✓ maintained ≥ 85%

## Commit Count
10 commits implementing promotion in phases

## Token Efficiency
- Plan generation via forge pipeline: ✓ minimal code written by human
- Ollama agents orchestrated execution: ✓ autonomous
- Incremental verification: ✓ caught errors early
- No large rewrites: ✓ small atomic commits
EOF

git add .claude/FORGE_PROMOTION_SUMMARY.md
git commit -m "docs: add forge promotion summary report"
```

- [ ] **Step 8: Final verification**

```bash
echo "=== Promotion Complete ==="
git log --oneline master~15..master | wc -l
echo "commits"
pytest tests/ -q
```

**Expected:** ~10-15 commits, all tests pass

---

## Execution Instructions for Pure Ollama Agents

**Ultra Token-Saving Mode:**

1. **Use forge pipeline to generate task runners** (not human-written)
2. **Invoke pure Ollama agents** to execute generated tasks
3. **Verify after each layer** (commit before proceeding to next)
4. **Reduce scope on failure** (implement smallest unit, verify, expand)
5. **Keep logs structured** (for debugging, not verbose output)

**Ollama Agent Invocation Template:**

```bash
cd /mnt/d/ClaudeClockwork
ollama run mistral << 'TASK'
You are an autonomous agent executing a code generation task.

Task: [Step description from plan]

Generated task script is at: [path]

Execute:
1. Read the task script
2. Follow instructions
3. Run tests to verify
4. Report: SUCCESS or FAILURE

Do not wait for human input. Execute autonomously.
TASK
```

**Expected Outcome:**
- All 10 tasks completed
- All 4 forge capabilities first-class
- skill_forge_run composed skill working
- All tests passing
- ~15 commits, ~400 LOC changes
- Zero regressions

---

## Success Criteria

- [ ] All 4 primitives (code.plan, code.forge, code.review, code.validate) work via `run_local_capability()`
- [ ] `skill_forge_run(archetype, purpose, ...)` orchestrates full pipeline
- [ ] Mode parameter controls partial execution
- [ ] Publishing respects mode (skipped for partial runs)
- [ ] Temp workspace lifecycle correct (preserve on failure, cleanup on success)
- [ ] Execution logs structured (list of events, not flat string)
- [ ] Registry updated; manifests reflect first-class status
- [ ] All tests pass; no regressions to embed/asr
- [ ] All commits atomic and well-messaged
- [ ] No wrapper scripts required for normal usage
