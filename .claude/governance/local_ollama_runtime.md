# Local Ollama Runtime Governance

**Phase:** 22+
**Status:** BINDING
**Effective Date:** 2026-03-17

---

## Canonical Local Backend

### Windows Native Ollama

**Canonical configuration:**
- Backend: Windows native Ollama (not WSL, not Docker, not remote)
- Connection: `http://127.0.0.1:11434`
- Execution: GPU-first (NVIDIA/AMD GPU required for default mode)
- Single-GPU, single-model constraint

This is the **only** supported path for local Ollama in default mode. Do not use alternatives without explicit override.

### CPU-Only Local Execution (Degraded)

Existing CPU-only setups (7950X3D or similar) are now classified as **degraded paths** and require:
- Explicit user acknowledgment
- Marking in execution logs as non-canonical
- No automatic selection as the default

CPU-only execution is still supported in `adaptive` and `claude-min` modes, but not as the canonical default.

---

## Mandatory Constraints

### 1. GPU-First Execution

- Default mode requires GPU-capable Ollama
- Models must be GPU-accelerated (qwen3:8b, phi4, etc.)
- CPU-only inference **prohibited** in default mode
- **Violation:** `ModeViolationError("Local Ollama must use GPU")`

### 2. Forbidden Model Escalations

Do **not** automatically escalate to:
- `qwen2.5:32b`, `qwen2.5-coder:32b`
- `qwen2.5:70b`, `qwen2.5-72b`
- `llama3.3:70b`, `llama2:70b`

These violate the single-GPU, single-model constraint. They require:
1. **Explicit user request** (not automatic routing)
2. Separate GPU or mixed precision (unmanaged memory)
3. CPU offload (against GPU-first principle)

**Violation:** `RuntimeError("Forbidden escalation to 32B/70B/72B")`

### 3. Single GPU, Single Model

- `num_parallel: 1` — one inference at a time
- `max_loaded_models: 1` — one model in VRAM
- No model juggling, no background unloading
- Warm reuse preferred to avoid reload delays

### 4. Hard Timeout Enforcement

| Timeout | Seconds | Purpose |
|---------|---------|---------|
| `connect_timeout` | 10 | Establish TCP connection |
| `health_timeout` | 15 | Health check (model list) |
| `request_timeout` | 300 | Standard inference (5 min) |
| `heavy_timeout` | 600 | Large context (10 min) |
| `warmup_timeout` | 120 | Load model to VRAM (2 min) |
| `agent_step_timeout` | 420 | Single agent step (7 min) |

**Violation:** `TimeoutError("Ollama request exceeded {timeout_name}")`

---

## Mode Compliance

### Default Mode

| Constraint | Status | Enforcement |
|-----------|--------|-------------|
| GPU-first | REQUIRED | Hard gate |
| Forbidden escalations | BLOCKED | Error on attempt |
| Single model | ENFORCED | `num_parallel=1` |
| Timeouts | HARD LIMIT | Fail on exceed |
| CPU-only fallback | FORBIDDEN | No degradation |

**Availability Behavior:** If Ollama unavailable → fail closed (no fallback to Claude).

### Adaptive Mode

| Constraint | Status | Enforcement |
|-----------|--------|-------------|
| GPU-first | PREFERRED | Soft default |
| Forbidden escalations | FORBIDDEN | Error on attempt |
| Single model | ENFORCED | Still `num_parallel=1` |
| Timeouts | HARD LIMIT | Fail on exceed |
| CPU-only fallback | ALLOWED | With warning |

**Availability Behavior:** If Ollama unavailable → may escalate to Claude (not forced).

### Claude-Min Mode

| Constraint | Status | Enforcement |
|-----------|--------|-------------|
| GPU-first | N/A | Not applicable |
| Forbidden escalations | N/A | Not applicable |
| Single model | N/A | Not applicable |
| Timeouts | HARD LIMIT | Fail on exceed |
| Ollama | FORBIDDEN | No local execution |

---

## Operational Rules

### 1. Connection Validation

Always check connection before execution:
```python
def validate_connection(base_url="http://127.0.0.1:11434", timeout=10):
    """Verify Ollama is reachable."""
    # Read from .claude/config/local_ollama_runtime.yaml
    # Use connect_timeout_seconds from config
    # On failure: raise ModeViolationError if default mode
```

### 2. Model Whitelist Check

Before loading a model:
```python
def validate_model_allowed(model_name):
    """Check model against forbidden_escalations."""
    config = load_local_runtime_config()
    if model_name in config['models']['forbidden_escalations']:
        raise RuntimeError(f"Forbidden escalation: {model_name}")
```

### 3. GPU-First Verification

Verify GPU availability:
```python
def verify_gpu_first():
    """Ensure GPU will be used."""
    config = load_local_runtime_config()
    if config['runtime']['gpu_first_required']:
        # Check nvidia-smi or equivalent
        # On failure: raise ModeViolationError in default mode
```

### 4. Timeout Enforcement

All Ollama requests use config timeouts:
```python
def apply_timeouts(operation_type):
    """Get timeout from config based on operation."""
    config = load_local_runtime_config()
    timeout_key = f"{operation_type}_timeout_seconds"
    return config['timeouts'][timeout_key]
```

---

## Configuration Hierarchy

### Single Source of Truth (SSOT)

The canonical definition is **`.claude/config/local_ollama_runtime.yaml`**.

### Resolution Order

1. `local_ollama_runtime.yaml` — **PRIMARY** (this file's config)
2. `.claude/config/ollama.yaml` — Secondary (model profiles only)
3. Mode profile overrides — Tertiary (only if explicit in mode)
4. Runtime defaults — Fallback

**Important:** Do NOT let routing configs, Claude tier settings, or other modules override the local runtime config.

---

## Enforcement Gates

These gates are checked in order by all Ollama execution paths:

```
1. Connection Validation
   └─ Is Ollama reachable at 127.0.0.1:11434?
   └─ (connect_timeout_seconds applies)

2. Mode Validation
   └─ Is local execution allowed in active mode?
   └─ (default: required; adaptive: allowed; claude-min: forbidden)

3. Model Whitelist
   └─ Is the requested model allowed?
   └─ (check forbidden_escalations list)

4. GPU-First Validation
   └─ Is GPU available? (default mode only)
   └─ (check nvidia-smi, check runtime.gpu_first_required)

5. Token Limit Validation
   └─ Does num_ctx respect tier_limits?
   └─ (8B models: max 4096; larger: forbidden or fail)

6. Timeout Enforcement
   └─ Is the request within operation timeout?
   └─ (fail on exceed, no grace period)
```

---

## Documentation Updates

### For Users

"Local Ollama execution now requires GPU. CPU-only inference has been moved to degraded paths. If you have a CPU-only system, use `adaptive` mode to allow fallback to Claude API."

### For Developers

"All local Ollama execution must validate against `.claude/config/local_ollama_runtime.yaml`. This is the SSOT for connection, model selection, timeouts, and GPU constraints. Do not hardcode Ollama URLs or timeouts anywhere else."

### For Operations

"Windows native Ollama at 127.0.0.1:11434 is the canonical local backend. CPU-only setups are supported in adaptive mode but not recommended as default. Monitor health checks at 5-minute intervals."

---

## Violation Examples

### Example 1: Forbidden Escalation (Default Mode)

```python
# User requests planning, which normally uses 70B
active_mode = "default"  # GPU-first required
requested_model = "qwen2.5:72b"  # In forbidden_escalations

# Violation check:
config = load_local_runtime_config()
if requested_model in config['models']['forbidden_escalations']:
    raise RuntimeError(
        "Forbidden escalation to 70B models in default mode. "
        "GPU-first execution required. Use adaptive mode for fallback."
    )
```

### Example 2: Timeout Exceeded

```python
# Standard request takes 400 seconds
request_timeout = 300  # From config.timeouts.request_timeout_seconds

# Violation:
if elapsed_time > request_timeout:
    raise TimeoutError(
        f"Ollama request exceeded {request_timeout} seconds. "
        f"Elapsed: {elapsed_time}s. Aborting."
    )
```

### Example 3: GPU-First Failure (Default Mode)

```python
# Default mode requires GPU
active_mode = "default"
gpu_available = check_nvidia_smi()  # Returns False

# Violation:
if not gpu_available and active_mode == "default":
    raise ModeViolationError(
        "Local Ollama requires GPU in default mode. "
        "No NVIDIA/AMD GPU detected. Use adaptive mode."
    )
```

---

## Monitoring & Audits

### Health Checks

- **Frequency:** Every 300 seconds (configurable)
- **On Startup:** Always run once
- **Model Used:** `config['models']['default_model']`
- **Timeout:** `health_timeout_seconds` (15 seconds)

### Logging

- All timeouts logged to stderr
- All escalation attempts logged
- All GPU checks logged
- All forbidden model requests logged

### Audit Trail

Operations that interact with Ollama should log:
- Model name
- Operation type (inference, warmup, health check)
- Elapsed time
- Timeout used
- GPU status

---

## Future Updates

This document is binding but not immutable. Updates require:
1. User notification
2. Test coverage for new constraints
3. Governance review
4. Version bump in `local_ollama_runtime.yaml`

Next review: 2026-04-01 or sooner if operational issues arise.
