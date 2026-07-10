# Mode System Hardening - Remaining Tasks Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete mode system integration by adding planner filtering, backfilling skill manifests with mode metadata, hardening routing logic, and documenting mode requirements.

**Architecture:** Four independent tasks executed via TDD. Planner adds mode-aware filtering at routing stage. Manifests backfilled with mode_requirements metadata. Router (if exists) adds mode validation mirroring executor gates. Docs updated with examples.

**Tech Stack:** Python 3.10+, pytest, SQLAlchemy, existing mode_manager/mode_guard/mode_validator/mode_audit classes.

---

## File Structure

### New Files
- `claudeclockwork/core/planner/mode_filter.py` - Mode-aware skill filtering logic
- `tests/test_mode_aware_planner.py` - Tests for planner filtering

### Modified Files
- `claudeclockwork/core/planner/*.py` - Integrate mode filter into existing planner
- `claudeclockwork/core/router/*.py` - (If router exists) Add mode validation gates
- Skill manifest files in `claudeclockwork/skills/*/manifest.json` - Backfill mode_requirements
- `.claude/docs/MANIFEST_SCHEMA.md` - Add mode_requirements documentation
- `claudeclockwork/core/mode/__init__.py` - Export mode filter if created as utility

### Test Files
- `tests/test_mode_aware_planner.py` - Planner filtering tests (task 1)
- `tests/test_mode_system.py` - Add 5-10 tests for manifest validation, router hardening (tasks 2-3)

---

## Chunk 1: Mode-Aware Planner Filter

### Task 1: Implement Mode-Aware Planner Filtering

**Files:**
- Create: `claudeclockwork/core/planner/mode_filter.py`
- Modify: `claudeclockwork/core/planner/__init__.py` (or main planner file)
- Test: `tests/test_mode_aware_planner.py`

#### Background

The planner suggests/routes skills for execution. Before routing, it must filter out skills incompatible with the active mode. For example, in `default` mode (Pure Ollama), the planner must not suggest Claude-only skills.

**Mode constraints:**
- `default`: Allow only `agent_type == "ollama"`
- `adaptive`: Allow `agent_type in ["ollama", "claude", "hybrid"]`
- `claude-min`: Allow only `agent_type == "claude"`

#### Implementation Steps

- [ ] **Step 1: Explore existing planner structure**

Run:
```bash
cd /mnt/d/ClaudeClockwork
find . -path ./\.git -prune -o -name "*planner*.py" -type f -print
```

Expected: Find planner files (e.g., `claudeclockwork/core/planner/*.py` or similar)

- [ ] **Step 2: Read planner entry point to understand skill filtering logic**

Identify where the planner decides which skills are available/suggested. Look for:
- Method that returns available skills
- Where filtering happens (if at all)
- How manifests are accessed

- [ ] **Step 3: Write failing test for mode-aware filtering**

Create `tests/test_mode_aware_planner.py`:

```python
import pytest
from claudeclockwork.core.mode import ModeManager
from claudeclockwork.core.planner.mode_filter import apply_mode_filter

def test_default_mode_filters_out_claude_skills():
    """In default mode, Claude skills should be filtered out."""
    manager = ModeManager()
    manager.set_active_mode("default")

    skills = [
        {"id": "skill1", "metadata": {"mode_requirements": {"agent_type": "ollama"}}},
        {"id": "skill2", "metadata": {"mode_requirements": {"agent_type": "claude"}}},
        {"id": "skill3", "metadata": {"mode_requirements": {"agent_type": "hybrid"}}},
    ]

    filtered = apply_mode_filter(skills, manager.get_active_mode())

    assert len(filtered) == 1
    assert filtered[0]["id"] == "skill1"

def test_adaptive_mode_allows_all_skills():
    """In adaptive mode, all agent types should be allowed."""
    manager = ModeManager()
    manager.set_active_mode("adaptive")

    skills = [
        {"id": "skill1", "metadata": {"mode_requirements": {"agent_type": "ollama"}}},
        {"id": "skill2", "metadata": {"mode_requirements": {"agent_type": "claude"}}},
        {"id": "skill3", "metadata": {"mode_requirements": {"agent_type": "hybrid"}}},
    ]

    filtered = apply_mode_filter(skills, manager.get_active_mode())

    assert len(filtered) == 3

def test_claude_min_mode_filters_out_ollama_skills():
    """In claude-min mode, only Claude skills should be allowed."""
    manager = ModeManager()
    manager.set_active_mode("claude-min")

    skills = [
        {"id": "skill1", "metadata": {"mode_requirements": {"agent_type": "ollama"}}},
        {"id": "skill2", "metadata": {"mode_requirements": {"agent_type": "claude"}}},
        {"id": "skill3", "metadata": {"mode_requirements": {"agent_type": "hybrid"}}},
    ]

    filtered = apply_mode_filter(skills, manager.get_active_mode())

    assert len(filtered) == 1
    assert filtered[0]["id"] == "skill2"

def test_missing_mode_requirements_excluded():
    """Skills without mode_requirements should be excluded (fail closed)."""
    manager = ModeManager()
    manager.set_active_mode("default")

    skills = [
        {"id": "skill1", "metadata": {"mode_requirements": {"agent_type": "ollama"}}},
        {"id": "skill2", "metadata": {}},  # Missing mode_requirements
    ]

    filtered = apply_mode_filter(skills, manager.get_active_mode())

    assert len(filtered) == 1
    assert filtered[0]["id"] == "skill1"
```

Run:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_aware_planner.py -v
```

Expected: FAIL (module/function doesn't exist yet)

- [ ] **Step 4: Implement mode_filter.py**

Create `claudeclockwork/core/planner/mode_filter.py`:

```python
"""Mode-aware skill filtering for planner routing."""
from __future__ import annotations

from typing import Any

from claudeclockwork.core.mode import ModeManager


def apply_mode_filter(skills: list[dict[str, Any]], active_mode: str) -> list[dict[str, Any]]:
    """
    Filter skills by active mode constraints.

    Args:
        skills: List of skill manifest dicts
        active_mode: Active mode name (default, adaptive, claude-min)

    Returns:
        Filtered list of compatible skills
    """
    manager = ModeManager()
    mode_config = manager.get_mode_config(active_mode)

    filtered = []
    for skill in skills:
        # Fail closed: missing mode_requirements excluded
        mode_requirements = skill.get("metadata", {}).get("mode_requirements")
        if not mode_requirements:
            continue

        agent_type = mode_requirements.get("agent_type")

        # Check agent_type against mode constraints
        if agent_type == "ollama" and mode_config.get("allow_ollama"):
            filtered.append(skill)
        elif agent_type == "claude" and mode_config.get("allow_claude"):
            filtered.append(skill)
        elif agent_type == "hybrid" and mode_config.get("allow_mixed"):
            filtered.append(skill)
        # else: skill incompatible with mode, excluded

    return filtered


def integrate_mode_filter_into_planner(planner_class_or_function) -> Any:
    """
    Decorator/wrapper to add mode filtering to planner's get_available_skills() or similar.

    Usage:
        @integrate_mode_filter_into_planner
        def get_available_skills(context):
            # ... existing logic ...
            all_skills = registry.list_all()
            # After this, apply mode filter:
            return apply_mode_filter(all_skills, active_mode)
    """
    # This will be called by planner integration task
    # For now, just provide the helper function above
    pass
```

- [ ] **Step 5: Run tests to verify they pass**

Run:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_aware_planner.py -v
```

Expected: PASS (all 4 tests)

- [ ] **Step 6: Integrate mode filter into planner**

Locate the planner's skill filtering logic (likely in `get_available_skills()` or `_get_candidates()` or similar). Add call to `apply_mode_filter()`:

```python
from claudeclockwork.core.planner.mode_filter import apply_mode_filter

# Before routing/suggesting skills:
all_skills = self.registry.get_all()  # or however skills are fetched
mode_aware_skills = apply_mode_filter(all_skills, ModeManager().get_active_mode())

# Use mode_aware_skills instead of all_skills for routing
```

- [ ] **Step 7: Run all mode tests to ensure no regressions**

Run:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_system.py tests/test_mode_aware_planner.py -v
```

Expected: All tests pass (44+ tests)

- [ ] **Step 8: Commit**

```bash
cd /mnt/d/ClaudeClockwork
git add claudeclockwork/core/planner/mode_filter.py tests/test_mode_aware_planner.py claudeclockwork/core/planner/__init__.py
git commit -m "feat: add mode-aware skill filtering to planner

- Implement apply_mode_filter() to exclude incompatible skills
- Filter by active mode constraints (ollama, claude, mixed)
- Fail closed: missing mode_requirements excluded
- Add 4 tests: default mode, adaptive mode, claude-min mode, missing metadata
- Integrate into planner's skill routing logic"
```

---

## Chunk 2: Manifest Backfill

### Task 2: Backfill Existing Skill Manifests with Mode Requirements

**Files:**
- Skill manifest files: `claudeclockwork/skills/*/manifest.json` (or .yaml)
- Test: `tests/test_mode_system.py` (add backfill validation tests)

#### Background

All existing skills must declare `mode_requirements` in their manifests. Without this, the mode validator will fail closed and skills won't execute.

**mode_requirements structure:**
```json
{
  "mode_requirements": {
    "agent_type": "ollama|claude|hybrid",
    "requires_mode": ["default", "adaptive", "claude-min"] or []
  }
}
```

#### Implementation Steps

- [ ] **Step 1: Inventory existing skills**

Run:
```bash
cd /mnt/d/ClaudeClockwork
find . -path ./\.git -prune -o -name "manifest.*" -type f -print | head -20
```

Expected: List of skill manifest files (format: JSON or YAML)

- [ ] **Step 2: Check which skills are missing mode_requirements**

Run:
```bash
cd /mnt/d/ClaudeClockwork
grep -L "mode_requirements" $(find . -path ./\.git -prune -o -name "manifest.*" -type f -print) | wc -l
```

Expected: Count of manifests missing mode_requirements

- [ ] **Step 3: Determine agent_type for each skill**

Review skill code/purpose:
- **ollama skills**: local inference, small models, cost-sensitive → `agent_type: "ollama"`
- **claude skills**: complex reasoning, code analysis, high-quality output → `agent_type: "claude"`
- **hybrid skills**: can use either, routing decides → `agent_type: "hybrid"`

Document your categorization.

- [ ] **Step 4: Write test validating all manifests have mode_requirements**

Add to `tests/test_mode_system.py`:

```python
def test_all_manifests_have_mode_requirements():
    """All skill manifests must declare mode_requirements."""
    registry = SkillRegistry()  # or however to load all manifests
    manifests = registry.get_all_manifests()

    missing = []
    for manifest in manifests:
        if "mode_requirements" not in manifest.get("metadata", {}):
            missing.append(manifest.get("id", "unknown"))

    assert len(missing) == 0, f"Manifests missing mode_requirements: {missing}"
```

Run:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_system.py::test_all_manifests_have_mode_requirements -v
```

Expected: FAIL (manifests missing mode_requirements)

- [ ] **Step 5: Backfill mode_requirements in all manifests**

For each manifest file, add `mode_requirements` to `metadata`. Example:

**Before:**
```json
{
  "id": "code_plan",
  "name": "Code Planner",
  "metadata": {
    "version": "1.0"
  }
}
```

**After:**
```json
{
  "id": "code_plan",
  "name": "Code Planner",
  "metadata": {
    "version": "1.0",
    "mode_requirements": {
      "agent_type": "ollama",
      "requires_mode": []
    }
  }
}
```

Batching: Use a script or do manually based on skill count. Ensure consistency.

- [ ] **Step 6: Run backfill validation test**

Run:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_system.py::test_all_manifests_have_mode_requirements -v
```

Expected: PASS

- [ ] **Step 7: Run full test suite**

Run:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_system.py -v
```

Expected: All tests pass (44+ tests)

- [ ] **Step 8: Commit**

```bash
cd /mnt/d/ClaudeClockwork
git add claudeclockwork/skills/*/manifest.*
git add tests/test_mode_system.py
git commit -m "feat: backfill all skill manifests with mode_requirements

- Add mode_requirements to all skill manifest files
- Categorize by agent_type: ollama (local), claude (reasoning), hybrid (adaptive)
- Ensure mode_validator passes for all existing skills
- Add validation test: test_all_manifests_have_mode_requirements"
```

---

## Chunk 3: Router Hardening (Conditional)

### Task 3: Harden Router with Mode Validation (If Router Exists)

**Files:**
- `claudeclockwork/core/router/*.py` (if exists)
- Test: `tests/test_mode_system.py` (add router tests)

#### Background

If a router exists (determines which LLM handles a skill), it must validate mode constraints. Add mode checks mirroring executor gates:
1. Validate active mode state
2. Check skill is compatible with mode
3. Return error if incompatible (don't silently fall through)

#### Implementation Steps

- [ ] **Step 1: Check if router exists**

Run:
```bash
cd /mnt/d/ClaudeClockwork
find . -path ./\.git -prune -o -type f -name "*router*.py" -print
```

If no files found: **SKIP THIS TASK** (no router to harden).
If files found: Continue.

- [ ] **Step 2: Read router code to understand routing logic**

Identify:
- Where routing decision is made
- What happens if mode constraint violated
- Current error handling

- [ ] **Step 3: Write test for mode-aware routing**

Add to `tests/test_mode_system.py`:

```python
def test_router_respects_mode_constraints():
    """Router should reject skills incompatible with active mode."""
    router = Router()  # or OllamaRouter, etc.
    manager = ModeManager()
    manager.set_active_mode("default")  # Ollama only

    # Try to route a Claude-only skill
    skill_manifest = {
        "id": "claude_skill",
        "metadata": {"mode_requirements": {"agent_type": "claude"}}
    }

    result = router.route(skill_manifest)

    # Should fail or return error, not silently fall through
    assert result.get("error") or not result.get("success")

def test_router_validates_mode_state():
    """Router should validate mode state before routing."""
    router = Router()
    # Corrupt mode state somehow (this is artificial for testing)

    result = router.route(any_skill_manifest)

    # Should fail if mode state invalid
    assert "mode" in str(result.get("error", "")).lower()
```

- [ ] **Step 4: Add mode validation to router**

In the router's route() method or equivalent, add before deciding which LLM:

```python
from claudeclockwork.core.mode import ModeGuard, ModeViolationError, ModeManager

def route(self, skill_manifest):
    # Validate mode state
    mode_manager = ModeManager()
    mode_guard = ModeGuard(mode_manager)

    try:
        # Get mode requirements from manifest
        agent_type = skill_manifest.get("metadata", {}).get("mode_requirements", {}).get("agent_type")

        # Check mode constraints
        if agent_type == "claude":
            mode_guard.check_claude_execution_allowed()
        elif agent_type == "ollama":
            mode_guard.check_ollama_execution_allowed()
        elif agent_type == "hybrid":
            mode_guard.check_mixed_execution_allowed()

    except ModeViolationError as e:
        return {"success": False, "error": str(e)}

    # If we get here, mode check passed; continue with routing logic
    # ... existing routing logic ...
```

- [ ] **Step 5: Run router mode tests**

Run:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_system.py::test_router_respects_mode_constraints -v
pytest tests/test_mode_system.py::test_router_validates_mode_state -v
```

Expected: PASS

- [ ] **Step 6: Run full test suite**

Run:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_system.py -v
```

Expected: All tests pass

- [ ] **Step 7: Commit**

```bash
cd /mnt/d/ClaudeClockwork
git add claudeclockwork/core/router/*.py tests/test_mode_system.py
git commit -m "feat: add mode validation to router

- Router now validates mode constraints before routing
- Mirrors executor hard-gates (claude, ollama, mixed)
- Fails closed: incompatible skills return error instead of silent bypass
- Add 2 tests: mode-aware routing, mode state validation"
```

---

## Chunk 4: Documentation

### Task 4: Document Mode Requirements in Manifest Schema

**Files:**
- `.claude/docs/MANIFEST_SCHEMA.md` (or equivalent documentation)
- `CLAUDE.md` (update with mode system summary)

#### Background

Developers need clear guidance on what `mode_requirements` is, why it's required, and examples of correct usage.

#### Implementation Steps

- [ ] **Step 1: Locate/create manifest schema documentation**

Run:
```bash
cd /mnt/d/ClaudeClockwork
find . -path ./\.git -prune -o -type f -name "MANIFEST*" -o -name "*schema*" -print | grep -i manifest
```

Expected: Find existing schema doc or identify where to create it.

- [ ] **Step 2: Write test ensuring documentation exists**

(Documentation is prose; test is a sanity check)

```python
def test_manifest_schema_documentation_exists():
    """Manifest schema documentation should exist and mention mode_requirements."""
    import os
    doc_path = ".claude/docs/MANIFEST_SCHEMA.md"
    assert os.path.exists(doc_path), f"Schema doc missing: {doc_path}"

    with open(doc_path) as f:
        content = f.read()

    assert "mode_requirements" in content.lower(), "Schema doc must mention mode_requirements"
    assert "agent_type" in content.lower(), "Schema doc must mention agent_type"
```

- [ ] **Step 3: Add mode_requirements section to manifest schema documentation**

Add to `.claude/docs/MANIFEST_SCHEMA.md`:

```markdown
## mode_requirements (REQUIRED)

All skill manifests MUST include `mode_requirements` in metadata.

### Structure

```json
{
  "metadata": {
    "mode_requirements": {
      "agent_type": "ollama|claude|hybrid",
      "requires_mode": ["mode1", "mode2"]
    }
  }
}
```

### Fields

- **agent_type** (required): Which AI system(s) execute this skill
  - `"ollama"` - Local Ollama inference only (cost: $0, latency: CPU-bound)
  - `"claude"` - Claude API only (cost: $0.08-15/1M tokens depending on model)
  - `"hybrid"` - Can use either; router decides based on cost/performance

- **requires_mode** (optional): Restrict to specific modes
  - `[]` (default) - Skill works in all modes
  - `["default", "adaptive"]` - Only in these modes
  - Fail-closed: if mode not in list, skill is rejected

### Examples

**Ollama-only skill** (local inference, small models):
```json
{
  "id": "code_formatter",
  "metadata": {
    "mode_requirements": {
      "agent_type": "ollama",
      "requires_mode": []
    }
  }
}
```

**Claude-only skill** (complex reasoning, high-quality output):
```json
{
  "id": "code_architect",
  "metadata": {
    "mode_requirements": {
      "agent_type": "claude",
      "requires_mode": []
    }
  }
}
```

**Hybrid skill** (router decides):
```json
{
  "id": "code_review",
  "metadata": {
    "mode_requirements": {
      "agent_type": "hybrid",
      "requires_mode": []
    }
  }
}
```

**Mode-specific skill** (only in adaptive mode):
```json
{
  "id": "multi_llm_consensus",
  "metadata": {
    "mode_requirements": {
      "agent_type": "hybrid",
      "requires_mode": ["adaptive"]
    }
  }
}
```

### Validation

- Missing `mode_requirements` → Execution fails (fail-closed)
- Unknown `agent_type` → Execution fails
- Mode not in `requires_mode` → Skill filtered out by planner/executor
```

- [ ] **Step 4: Update CLAUDE.md with mode system summary**

Add to `CLAUDE.md`:

```markdown
## Mode System

The ClaudeClockwork framework enforces a hard /mode system with three execution modes:

| Mode | Ollama | Claude | Mixed | Use Case |
|------|--------|--------|-------|----------|
| **default** | ✅ Only | ❌ | ❌ | Budget-first; pure local inference |
| **adaptive** | ✅ | ✅ | ✅ | Flexible; use best tool for job |
| **claude-min** | ❌ | ✅ | ❌ | Reasoning-heavy; high-quality output |

**Critical rule:** Mode is binding. No bypasses, fallbacks, or exceptions.

### For Skill Developers

Every skill manifest MUST declare mode_requirements:

```json
{
  "metadata": {
    "mode_requirements": {
      "agent_type": "ollama|claude|hybrid",
      "requires_mode": []
    }
  }
}
```

See `.claude/docs/MANIFEST_SCHEMA.md` for full schema and examples.

### For Users

Change mode with `/mode set default|adaptive|claude-min`. View current mode: `/mode show`.

Audit mode system: `/mode audit` (checks state, config, constraints, persistence).

### Implementation

- **Manager** (`ModeManager`) - Lifecycle & configuration
- **Guard** (`ModeGuard`) - Hard-gates; throws `ModeViolationError` on violation
- **Validator** (`ModeMetadataValidator`) - Fail-closed metadata validation
- **Executor** (`SkillExecutor`) - 6 hard-gates before any execution
- **Planner** - Filters skills by mode before routing
- **Audit** (`ModeAudit`) - Self-checking capability

All changes must preserve fail-closed semantics: unknown/incomplete mode metadata causes execution failure, not silent bypass.
```

- [ ] **Step 5: Run documentation tests**

Run:
```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_system.py::test_manifest_schema_documentation_exists -v
```

Expected: PASS

- [ ] **Step 6: Verify documentation quality**

Manually review:
- `.claude/docs/MANIFEST_SCHEMA.md` - Clear examples? All fields explained?
- `CLAUDE.md` - Mode table correct? Examples accurate?

- [ ] **Step 7: Commit**

```bash
cd /mnt/d/ClaudeClockwork
git add .claude/docs/MANIFEST_SCHEMA.md CLAUDE.md tests/test_mode_system.py
git commit -m "docs: add mode_requirements documentation and examples

- Document mode_requirements structure in MANIFEST_SCHEMA.md
- Add 4 examples: ollama-only, claude-only, hybrid, mode-specific
- Update CLAUDE.md with mode system summary and developer guide
- Add documentation validation test"
```

---

## Final Verification

- [ ] **Run all mode tests**

```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_system.py tests/test_mode_aware_planner.py -v --tb=short
```

Expected: All tests pass (55+ tests)

- [ ] **Check coverage**

```bash
cd /mnt/d/ClaudeClockwork
pytest tests/test_mode_system.py tests/test_mode_aware_planner.py --cov=claudeclockwork/core/mode --cov=claudeclockwork/core/planner --cov-report=term-missing
```

Expected: >90% coverage for mode and planner modules

- [ ] **View commit log**

```bash
cd /mnt/d/ClaudeClockwork
git log --oneline -10
```

Expected: 4 commits (one per task) with clear messages

---

## Summary

**What was completed:**

1. ✅ **Mode-aware planner filter** - Skills filtered by mode before routing
2. ✅ **Manifest backfill** - All skills declare mode_requirements
3. ✅ **Router hardening** (if applicable) - Router validates mode constraints
4. ✅ **Documentation** - MANIFEST_SCHEMA.md and CLAUDE.md updated

**Testing:**
- 4 planner tests (default, adaptive, claude-min, missing metadata)
- 2 router tests (mode constraints, state validation) - if router exists
- 1 manifest validation test
- 1 documentation test
- All integrated with existing 44 mode system tests

**Code quality:**
- All changes follow existing patterns
- TDD approach: test first, implement, pass
- Fail-closed semantics maintained throughout
- No changes to hardened core (manager, guard, validator, audit, executor)

**Next steps:** Use superpowers:subagent-driven-development to execute this plan with fresh subagents per task.
