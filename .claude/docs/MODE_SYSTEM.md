# ClaudeClockwork Mode System

**Status:** Active
**Last Updated:** 2026-03-16
**Criticality:** HIGH — Mode is law

---

## Executive Summary

The ClaudeClockwork Mode System implements **persistent, binding execution mode enforcement**. Once a mode is active, it is a **hard runtime constraint** that cannot be bypassed, reinterpreted, or worked around.

**CRITICAL RULE:** Mode is law.

- Only the user may change the active mode
- The runtime enforcement is hard-coded, not advisory
- Violations raise `ModeViolationError` and halt execution
- No silent escalation, compensation, or bypass is permitted

---

## Modes

### 1. Default Mode: Pure Ollama Agent Mode

**Designation:** `default` (system startup default)

**Permission Matrix:**
| Operation | Allowed |
|---|---|
| Ollama execution | ✅ YES |
| Claude execution | ❌ FORBIDDEN |
| Mixed execution | ❌ FORBIDDEN |
| Claude fallback | ❌ FORBIDDEN |

**Guarantees:**
- 100% Ollama agents, no Claude involvement
- Freezes if Ollama required but unavailable (`require_ollama_available=true`)
- No fallback to Claude under any circumstances
- No mixed orchestration paths

**Use Cases:**
- Cost-sensitive workflows (Ollama = $0)
- Environments where Claude API is not available
- Pure autonomous agent orchestration
- Offline or air-gapped deployments

**Hard Constraints Enforced:**
```python
# These raise ModeViolationError:
run_claude_agent(...)           # ❌ FORBIDDEN
run_mixed_orchestration(...)    # ❌ FORBIDDEN
use_claude_fallback(...)        # ❌ FORBIDDEN
```

### 2. Adaptive Mode: Claude + Ollama

**Designation:** `adaptive`

**Permission Matrix:**
| Operation | Allowed |
|---|---|
| Ollama execution | ✅ YES |
| Claude execution | ✅ YES |
| Mixed execution | ✅ YES |
| Claude fallback | ✅ YES |
| Allowed models | All (Haiku, Sonnet, Opus) |

**Guarantees:**
- Both Ollama and Claude available
- Mixed orchestration allowed (e.g., Ollama + Claude for complex reasoning)
- Claude fallback when Ollama unavailable
- Full model range available

**Use Cases:**
- Hybrid orchestration (Ollama for tasks, Claude for reasoning)
- Flexibility when tool availability varies
- Complex reasoning + autonomous execution
- Standard production deployments

**Usage Pattern:**
```python
# All of these are allowed:
run_ollama_agent(...)
run_claude_agent(...)
run_mixed_orchestration(...)
use_claude_fallback_on_ollama_fail(...)
```

### 3. Claude-Min Mode: Cheap Claude Only

**Designation:** `claude-min`

**Permission Matrix:**
| Operation | Allowed |
|---|---|
| Ollama execution | ❌ FORBIDDEN |
| Claude execution | ✅ YES (Haiku only) |
| Mixed execution | ❌ FORBIDDEN |
| Claude fallback | ❌ N/A (Claude-only) |
| Allowed models | `claude-haiku-4-5` only |
| Token budget | 100,000 max |

**Guarantees:**
- Claude Haiku only (cheapest model: ~$0.08/1M tokens)
- No Ollama integration
- No mixed execution
- Token budget enforced per operation
- Cost-effective for simple tasks

**Hard Constraints Enforced:**
```python
# These raise ModeViolationError:
run_ollama_agent(...)                # ❌ FORBIDDEN
use_claude_sonnet_or_opus(...)      # ❌ FORBIDDEN
run_operation_with_150k_tokens(...)  # ❌ FORBIDDEN (exceeds 100k budget)
```

**Use Cases:**
- Budget-constrained environments
- Simple Q&A and data processing
- Educational/development workflows
- Token-limited deployments

---

## Mode Governance

### 1. Mode is Binding

**The active mode is a hard runtime contract, not a guideline.**

- ❌ Claude must NOT bypass mode constraints
- ❌ Claude must NOT reinterpret mode restrictions
- ❌ Claude must NOT silently escalate around mode limits
- ❌ Claude must NOT compensate for mode constraints
- ✅ Claude MUST enforce mode constraints strictly
- ✅ Claude MUST raise `ModeViolationError` on violation attempts
- ✅ Claude MUST halt execution, never continue in violation

**Example: What NOT to Do in Default Mode**

```python
# ❌ WRONG: Attempting to work around default mode
try:
    run_claude_agent(...)  # This will raise ModeViolationError
except ModeViolationError:
    # ❌ WRONG: Do not try to compensate
    use_different_approach_that_also_violates_mode()

# ❌ WRONG: Reinterpreting the constraint
# "Maybe 'default mode forbids Claude' doesn't apply to internal uses"
# NO. Mode is binding in ALL contexts.

# ❌ WRONG: Escalating silently
# "Ollama unavailable, user didn't specify what to do, so I'll use Claude"
# NO. Default mode freezes if Ollama unavailable.
```

**Example: What TO DO**

```python
# ✅ CORRECT: Enforce mode strictly
try:
    result = run_ollama_agent(...)
except ModeViolationError as e:
    # Raise the error, don't suppress it
    raise e
except OllamaUnavailableError:
    # In default mode, this is a fatal error
    # Do not attempt to work around it
    raise ModeViolationError(
        "Ollama unavailable and default mode forbids Claude fallback"
    )
```

### 2. Mode Change Authority

**Only the user may change the active mode.**

- Users invoke `/mode set <mode>` to change modes
- The system persists the mode to `.claude/state/mode_state.json`
- Programmatic mode changes (outside user command) are forbidden
- Audit trail shows who changed mode and when

### 3. Mode Transition Rules

Not all mode transitions are allowed. Valid transitions:

```
default     ↔ adaptive ↔ claude-min
default     ↔ claude-min
(All transitions allowed with one exception per mode profile)
```

Invalid transitions raise `ValueError` with clear messaging.

### 4. No Implicit Mode Switching

**The runtime NEVER switches modes without user consent.**

- ❌ Do not switch modes to work around constraints
- ❌ Do not switch modes to retry failed operations
- ❌ Do not switch modes for "better performance"
- ✅ Raise an error and report the mode constraint
- ✅ Let the user decide if they want to change mode

---

## Architecture

### Files

| File | Purpose |
|---|---|
| `.claude/config/mode_profiles.yaml` | Canonical mode definitions |
| `.claude/state/mode_state.json` | Current active mode (persistent) |
| `claudeclockwork/core/mode/mode_manager.py` | Mode state management |
| `claudeclockwork/core/mode/mode_guard.py` | Hard-gate enforcement |
| `claudeclockwork/core/mode/__init__.py` | Package exports |
| `tests/test_mode_system.py` | Mode system tests |

### Core Classes

#### ModeManager

Manages mode state and configuration:

```python
from claudeclockwork.core.mode import ModeManager

manager = ModeManager()

# Get current mode
active = manager.get_active_mode()  # "default", "adaptive", or "claude-min"

# Get mode config
config = manager.get_mode_config("default")

# Change mode (user-invoked only)
manager.set_mode("adaptive")

# Query mode constraints
manager.is_mode_allowed("claude_execution")  # False in default mode
manager.get_allowed_models()                 # [] in default, [...] in others
manager.get_token_budget()                   # 100000 in claude-min
```

#### ModeGuard

Hard-gates operations based on active mode:

```python
from claudeclockwork.core.mode import ModeGuard, ModeViolationError

guard = ModeGuard()

# Check before executing operations
try:
    guard.check_claude_execution_allowed()
except ModeViolationError as e:
    # Mode forbids this operation
    raise e

# Guard specific operations
@guard.guard_operation("claude_execution")
def run_claude_agent(...):
    # Will raise ModeViolationError if not allowed
    ...

# Check specific constraints
guard.check_model_allowed("claude-haiku-4-5")      # OK in claude-min
guard.check_token_budget(50000)                     # OK in claude-min
guard.check_mixed_execution_allowed()               # Raises in default
```

### ModeViolationError

Raised when an operation violates the active mode:

```python
try:
    guard.check_claude_execution_allowed()
except ModeViolationError as e:
    print(e)  # "Claude execution is forbidden in default mode. This is a hard constraint."
    # DO NOT suppress, retry, or work around this error
    # Instead, report to user and halt
    raise
```

---

## Usage Examples

### CLI: Check Current Mode

```bash
# Built-in command
/mode show

# Output:
# Active Mode: default (Pure Ollama Agent Mode)
# Constraints:
#   - Claude execution: FORBIDDEN
#   - Mixed execution: FORBIDDEN
#   - Ollama execution: ALLOWED
```

### CLI: List Available Modes

```bash
/mode list

# Output:
# Available modes:
#   default    — Pure Ollama Agent Mode
#   adaptive   — Claude + Ollama Hybrid Mode
#   claude-min — Claude Haiku Only (Cheap)
```

### CLI: Change Mode

```bash
# User command (only way to change mode)
/mode set adaptive

# Output:
# Mode changed: default → adaptive
# New constraints active immediately
```

### Code: Check Before Claude Operation

```python
from claudeclockwork.core.mode import ModeGuard, ModeViolationError

guard = ModeGuard()

try:
    guard.check_claude_execution_allowed()
    # Safe to use Claude
    result = run_claude_agent(...)
except ModeViolationError as e:
    # Mode forbids Claude, must not attempt workaround
    logger.error(f"Mode violation: {e}")
    raise
```

### Code: Adaptive Fallback Pattern (Only in Adaptive Mode)

```python
from claudeclockwork.core.mode import ModeGuard, ModeViolationError

guard = ModeGuard()

# This pattern ONLY works in adaptive mode
try:
    result = run_ollama_agent(...)
except OllamaUnavailableError:
    # Only allowed in adaptive mode
    guard.check_claude_execution_allowed()  # Will raise if not in adaptive
    result = run_claude_agent(...)
```

---

## Testing

All mode constraints are tested:

```bash
pytest tests/test_mode_system.py -v

# Tests cover:
# - Mode loading and persistence
# - Mode transitions and validation
# - Operation allowlists per mode
# - Hard constraint enforcement
# - Model allowlists and token budgets
# - Integration workflows
# - Mode binding guarantees
```

**Key regression test:**

```python
def test_mode_is_binding():
    """Test that mode constraints are binding (cannot be bypassed)."""
    manager = ModeManager()
    manager.set_mode("default")
    guard = ModeGuard(manager)

    # Attempting to bypass mode constraint must fail
    with pytest.raises(ModeViolationError):
        guard.check_claude_execution_allowed()
    # No way around it — error is raised, execution halted
```

---

## Design Decisions

### Why Hard-Gates, Not Advisories?

**Rationale:** Soft constraints (warnings, suggestions) can be ignored. Hard gates (exceptions) enforce discipline.

- If mode is "law," it must be enforced at the runtime level
- Violations must raise exceptions that halt execution
- No silent degradation or workaround paths

### Why Persistent Mode State?

**Rationale:** Mode preference persists across sessions.

- File: `.claude/state/mode_state.json`
- Loaded on startup
- Survives process restarts
- Audit trail (timestamp of last change)

### Why Three Modes?

**Rationale:** Cover the common cases.

| Mode | Use Case |
|---|---|
| default | Cost minimization, offline, autonomy |
| adaptive | Flexibility, hybrid orchestration, production |
| claude-min | Education, development, strict budgets |

Fewer modes = simpler. More modes = overcomplicated.

### Why No "Bypass" Escape Hatch?

**Rationale:** Law is law.

- If users could bypass modes, mode is not law, it's advice
- "Emergency override" scenarios are user-initiated mode changes, not escapes
- The user can invoke `/mode set adaptive` if they need flexibility

---

## Enforcement Checklist

Before committing code, verify:

- [ ] No Claude imports in default-mode-only paths
- [ ] No mixed execution orchestration in default mode
- [ ] No silent fallback to Claude in default mode
- [ ] `ModeViolationError` raised (not logged, not suppressed)
- [ ] Mode checked at operation entry, not inside try/except
- [ ] All mode changes go through user CLI (`/mode set`), never programmatic
- [ ] Tests verify mode binding (violations raise exceptions)
- [ ] Documentation states "mode is binding" clearly

---

## Summary

The Mode System enforces a **hard runtime contract** on execution patterns:

- **default mode:** Ollama only, no Claude, no mixed
- **adaptive mode:** Claude + Ollama hybrid, full flexibility
- **claude-min mode:** Cheap Claude (Haiku) only, no Ollama

**Mode is binding.** Violations raise exceptions. No workarounds. No compensation. No escalation.

Only the user may change the mode via `/mode set <mode>`.

