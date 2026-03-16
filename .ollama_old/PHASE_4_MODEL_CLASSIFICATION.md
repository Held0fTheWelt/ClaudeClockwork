# Phase 4: Model Classification & Safe ClaudeClockwork Mode

**Objective:** Define operating rules for using Ollama with ClaudeClockwork agents to prevent overload.

**Date:** March 16, 2026

**System Specs:**
- RAM: 64GB (Windows 11 Pro)
- GPU: NVIDIA RTX 3080 (10GB VRAM)
- Storage: E:\OllamaModels\.ollama (primary)
- Available GPU VRAM: 5.5GB free (at baseline)
- Ollama Setting: OLLAMA_NUM_PARALLEL=1 (enforces single inference)

---

## Part 1: Complete Model Classification

### Total Models Available: 60

#### TIER 1: ULTRA-SMALL (Embeddings Only)
**Use for:** Vector indexing, semantic search (non-inference)
**Max Parallel:** Unlimited (minimal compute)
**VRAM/RAM:** <500MB each
**Keep-alive:** Can be short (1-5 min)

```
nomic-embed-text:latest            0.26GB | 137M
mxbai-embed-large:latest           0.62GB | 334M
```

#### TIER 2: SMALL (≤8.5B parameters)
**Use for:** Fast context packing, summarization, quick docs, planning outlines
**Max Parallel:** 2-3 (with OLLAMA_NUM_PARALLEL=1, serialize these)
**VRAM/RAM:** 4-6GB each
**Keep-alive:** 15-30 minutes (frequently used)
**Inference Speed:** Fast (2-3 sec/token typical)

```
gemma3:latest                       3.11GB | 4.3B
qwen3-8b:validator                  4.87GB | 8.2B
qwen3-8b:reasoning                  4.87GB | 8.2B
qwen3:8b                            4.87GB | 8.2B
```

**Best For ClaudeClockwork:**
- `qwen3:8b` - General fast reasoning
- `qwen3-8b:validator` - Input validation, sanity checks
- `qwen3-8b:reasoning` - Small problem decomposition

---

#### TIER 3: MEDIUM (9-16B parameters)
**Use for:** Docs generation, secondary code review, creative tasks, embedding analysis
**Max Parallel:** 1-2 (serialize with OLLAMA_NUM_PARALLEL=1)
**VRAM/RAM:** 6-10GB each
**Keep-alive:** 20-45 minutes
**Inference Speed:** Moderate (1-2 sec/token typical)

```
llama3.2-vision:11b                 7.28GB | 10.7B
llama3.2-vision:creative            7.28GB | 10.7B
llama3.2-vision:reviewer            7.28GB | 10.7B
qwen2.5-14b:creative                8.37GB | 14.8B
qwen2.5-14b:docs                    8.37GB | 14.8B
qwen2.5-14b:agent                   8.37GB | 14.8B
qwen2.5:14b-instruct                8.37GB | 14.8B
deepseek-r1:14b                     8.37GB | 14.8B
phi4-14b:summarizer                 8.43GB | 14.7B
phi4-14b:docs                       8.43GB | 14.7B
phi4-14b:reviewer                   8.43GB | 14.7B
phi4-14b:validator                  8.43GB | 14.7B
phi4:14b                            8.43GB | 14.7B
```

**Best For ClaudeClockwork:**
- `qwen2.5-14b:docs` - Fast documentation generation
- `qwen2.5-14b:agent` - Task analysis, planning
- `phi4-14b:reviewer` - Secondary code review
- `deepseek-r1:14b` - Detailed reasoning on small problems

---

#### TIER 4: LARGE (15-36B parameters)
**Use for:** Main code implementation, architecture design, complex review, planning
**Max Parallel:** 1 (STRICT serialization)
**VRAM/RAM:** 16-26GB each
**Keep-alive:** 45min-2hr
**Inference Speed:** Slow (0.5-1 sec/token typical)
**WARNING:** Requires VRAM + swap management

```
devstral-small-2:latest             14.14GB | 24.0B
qwen3-coder:30b                     17.28GB | 30.5B
glm-4.7-flash:latest                17.71GB | 29.9B
glm-4.7-flash:creative              17.71GB | 29.9B
glm-4.7-flash:agent                 17.71GB | 29.9B
glm-4.7-flash:taskrunner            17.71GB | 29.9B
deepseek-r1:32b                     18.49GB | 32.8B
deepseek-coder:33b-instruct-q4_K_M  18.57GB | 33B
deepseek-coder-33b:reviewer         18.57GB | 33.3B
deepseek-coder-33b:coding           18.57GB | 33.3B
qwen2.5-coder:32b                   18.49GB | 32.8B
qwen2.5-coder-32b:integrator        18.49GB | 32.8B
qwen2.5-coder-32b:refactor          18.49GB | 32.8B
qwen2.5-coder-32b:reviewer          18.49GB | 32.8B
qwen2.5-coder-32b:coding            18.49GB | 32.8B
qwen3.5-35b:research                22.23GB | 36.0B
qwen3.5-35b:docs                    22.23GB | 36.0B
qwen3.5-35b:summarizer              22.23GB | 36.0B
qwen3.5-35b:integrator              22.23GB | 36.0B
qwen3.5-35b:reasoning               22.23GB | 36.0B
qwen3.5-35b:creative                22.23GB | 36.0B
qwen3.5-35b:planner                 22.23GB | 36.0B
qwen3.5-35b:agent                   22.23GB | 36.0B
qwen3.5-35b:taskrunner              22.23GB | 36.0B
qwen3.5:35b-a3b                     22.23GB | 36.0B
```

**Best For ClaudeClockwork:**
- `qwen2.5-coder-32b:coding` - Primary code implementation
- `qwen2.5-coder-32b:reviewer` - Independent review gate
- `deepseek-coder-33b:coding` - Alternative coding path
- `deepseek-coder-33b:reviewer` - Alternative review path
- `qwen3.5-35b:reasoning` - Complex planning
- `qwen3.5-35b:planner` - Orchestration planning

---

#### TIER 5: XLARGE (>36B parameters)
**Use for:** Strategic decisions, escalation judgment, architectural arbitration only
**Max Parallel:** 1 (STRICT serialization, high priority only)
**VRAM/RAM:** 40-50GB required
**Keep-alive:** 1-2 hours (rarely context-switched)
**Inference Speed:** Very slow (0.2-0.5 sec/token)
**CRITICAL:** Must have 20GB+ free RAM + GPU swap configured
**Caution Level:** ⚠️ EXTREME - Only invoke for tier-5 escalations

```
qwen2.5:72b-instruct-q4_K_M         44.16GB | 72.7B
qwen2.5-72b:docs                    44.16GB | 72.7B
qwen2.5-72b:summarizer              44.16GB | 72.7B
qwen2.5-72b:research                44.16GB | 72.7B
qwen2.5-72b:creative                44.16GB | 72.7B
qwen2.5-72b:escalation              44.16GB | 72.7B
qwen2.5-72b:reasoning               44.16GB | 72.7B
qwen2.5-72b:agent                   44.16GB | 72.7B
qwen2.5-72b:planner                 44.16GB | 72.7B
llama3.3:70b                        39.60GB | 70.6B
llama3.3:70b-instruct-q5_K_M        46.52GB | 70.6B
llama3.3-70b:summarizer             46.52GB | 70.6B
llama3.3-70b:escalation             46.52GB | 70.6B
llama3.3-70b:planner                46.52GB | 70.6B
llama3.3-70b:reasoning              46.52GB | 70.6B
llama3.3-70b:creative               46.52GB | 70.6B
```

**Best For ClaudeClockwork (Use Sparingly):**
- `qwen2.5-72b:escalation` - Escalation arbitration ONLY
- `qwen2.5-72b:reasoning` - Rare deep reasoning tasks (tier 5)
- `llama3.3-70b:escalation` - Alternative escalation path
- `llama3.3-70b:reasoning` - Alternative reasoning path

---

## Part 2: Safe ClaudeClockwork Operating Rules

### Core Principle
**Maximum 1 heavy inference at a time (OLLAMA_NUM_PARALLEL=1 enforces this).**

### Rule 1: Model Load Hierarchy

```
Priority 1 (ONLY):   TIER 5 (>36B) escalations
Priority 2:          TIER 4 (15-36B) implementation/review
Priority 3:          TIER 3 (9-16B) docs/creative
Priority 4:          TIER 2 (≤8.5B) validation/packing
Priority 5:          TIER 1 (embeddings) anytime
```

### Rule 2: Resource Guardrails

| Tier | Max Active | Min Free RAM | Min Free VRAM | Timeout | Recovery |
|------|-----------|--------------|---------------|---------|----------|
| 1    | Unlimited | 2GB          | N/A           | 60s     | Auto     |
| 2    | 1 seq     | 8GB          | 2GB           | 120s    | Auto     |
| 3    | 1 seq     | 16GB         | 3GB           | 180s    | Manual   |
| 4    | 1 seq     | 20GB         | 4GB           | 300s    | Manual   |
| 5    | 1 exclusive | 25GB       | 5GB           | 600s    | Restart  |

### Rule 3: Serialization Pattern

**NEVER load two Tier 4+ models in parallel. EVER.**

When a Tier 4+ model is requested:

1. **Check Status:** `curl http://localhost:11434/api/ps`
2. **If Empty:** Load model, wait for ready
3. **If Busy:**
   - Wait for current model to finish (up to timeout)
   - Call `OLLAMA_KEEP_ALIVE` unload: `curl -d '{"model":"current_model"}' http://localhost:11434/api/generate -X POST`
   - Then load new model
4. **If Timeout:** Manual intervention required

### Rule 4: Model Tier Usage Patterns

#### Tier 1 (Embeddings)
- Load any number in sequence
- Run indefinitely
- No resource conflict
- Never block higher tiers

#### Tier 2 (Small 8B)
- Max 1 active at a time
- Wait for unload before next
- Default keep-alive: 30 minutes
- After 30min with no requests: auto-unload
- Re-invoke: 752ms reload (mmap cached)

#### Tier 3 (Medium 14B)
- Max 1 active at a time
- Requires manual unload confirmation
- Default keep-alive: 45 minutes
- Check RAM before starting
- Re-invoke: 1-2 second reload

#### Tier 4 (Large 32B)
- **ABSOLUTE MAX: 1 only**
- Blocks all lower tiers
- Requires explicit RAM check (20GB+ free)
- 5-minute startup cost
- After 2 hours: forced unload + cleanup

#### Tier 5 (XLarge 70B+)
- **NEVER run unless escalation tier-5 decision required**
- Blocks everything else
- Requires 25GB+ free RAM
- 10-15 minute startup cost
- After 2 hours: **system restart recommended**

### Rule 5: Concurrency Rules

```
✓ ALLOWED COMBINATIONS:
  - Tier 1 + anything
  - Tier 2 + Tier 1
  - Tier 3 + Tier 1
  - Tier 4 + Tier 1
  - Tier 5 + nothing

✗ BLOCKED COMBINATIONS:
  - Tier 2 + Tier 2
  - Tier 2 + Tier 3+
  - Tier 3 + Tier 3+
  - Tier 4 + Tier 4+
  - Tier 5 + anything except Tier 1 (and even then, unload others first)
```

### Rule 6: Timeout & Recovery

#### Tier 2 Timeout (120 seconds)
- Auto-recover: Kill inference, unload model, free resources
- No manual action needed

#### Tier 3 Timeout (180 seconds)
- Alert operator: "Model timeout, manual unload required"
- Operator action: `ollama rm <model_name>` (soft)
- Recovery: Restart task or select lighter model

#### Tier 4+ Timeout (300-600 seconds)
- **CRITICAL ALERT**
- System may be hung
- Manual recovery:
  ```bash
  # 1. Stop Ollama gracefully
  curl -X POST http://localhost:11434/api/stop

  # 2. If that fails, restart Ollama
  taskkill /IM ollama.exe /F  # Windows

  # 3. Wait 30 seconds
  # 4. Start Ollama again
  # 5. Check status: curl http://localhost:11434/api/tags
  ```

### Rule 7: Memory Management

#### Free RAM Checks (Before Load)

```python
# Pseudocode for guardrails
import psutil

def can_load_model(tier):
    available_ram = psutil.virtual_memory().available
    if tier == 2 and available_ram < 8*GB: return False
    if tier == 3 and available_ram < 16*GB: return False
    if tier == 4 and available_ram < 20*GB: return False
    if tier == 5 and available_ram < 25*GB: return False
    return True
```

#### VRAM Checks (Before GPU Offload)

```
RTX 3080: 10GB total VRAM
Needed for RTX 3080 usage:
  - 2GB OS overhead (always reserved)
  - 3GB minimum model layer (at least one)
  - 5GB for SwapIn/SwapOut
  = 10GB baseline with 0GB free

Practical min for model loading: 5GB free
```

### Rule 8: Keep-Alive Tuning

**Current Setting:** `OLLAMA_KEEP_ALIVE=5m` (default)

**Recommended by Tier:**

| Tier | Recommended | Reason |
|------|-------------|--------|
| 1    | 1m          | Load instantly anyway |
| 2    | 30m         | Frequently reused, fast reload |
| 3    | 45m         | Moderate reuse, slower reload |
| 4    | 2h          | Expensive to reload, rare switches |
| 5    | Never keep  | Unload immediately after use |

**Implementation:**
```bash
# Per-model keep-alive (via API)
# When unloading a Tier 4 model after task completion:
curl -d '{"model":"qwen2.5-coder-32b:coding","keep_alive":"2h"}' \
  http://localhost:11434/api/generate

# When done for the day:
curl -d '{"model":"qwen2.5-coder-32b:coding","keep_alive":"0"}' \
  http://localhost:11434/api/generate
```

---

## Part 3: ClaudeClockwork Mode Definition

### Escalation Level → Model Tier Mapping

```
L0 (Specialist, autonomous, 1 file):
  → Tier 2 (qwen3:8b, phi4-14b:validator)

L1 (Team Lead, 2-5 files, clear boundaries):
  → Tier 3 (qwen2.5-14b:agent, phi4-14b:reviewer)

L2 (Architecture Agent, new module/dependency):
  → Tier 4 (qwen2.5-coder-32b:coding + code review)

L3 (Technical Critic, performance/external API):
  → Tier 4 (deepseek-coder-33b:reviewer)

L4 (Systemic Critic, governance/new agents):
  → Tier 4 escalation path + Tier 5 arbitration

L5 (User redesign/backend changes):
  → STOP & ASK (no model invocation)
  → If approved: Tier 5 (qwen2.5-72b:escalation)
```

### Recommended Model Selection by Task

#### Planning & Decomposition
```
L0: qwen3:8b (quick outline)
L1: qwen2.5-14b:agent (structured plan)
L2: qwen3.5-35b:planner (architecture)
L3+: qwen2.5-72b:planner (escalation reasoning)
```

#### Code Implementation
```
L0: N/A (escalate to L1)
L1: phi4-14b:validator (sanity check)
L2: qwen2.5-coder-32b:coding (primary)
L3: deepseek-coder-33b:coding (validation path)
L4: qwen3.5-35b:reasoning (judgement)
L5: qwen2.5-72b:reasoning (final arbitration)
```

#### Code Review (Independent Gate)
```
L0: qwen3:8b (structural review)
L1: phi4-14b:reviewer (detailed review)
L2: qwen2.5-coder-32b:reviewer (independent review)
L3: deepseek-coder-33b:reviewer (conflict resolution)
L4+: llama3.3-70b:reasoning (escalation review)
```

#### Documentation
```
L0: gemma3:latest (quick docs)
L1: qwen2.5-14b:docs (full docs)
L2: qwen3.5-35b:docs (architecture docs)
L3+: qwen2.5-72b:docs (comprehensive)
```

#### Summarization & Packing
```
Fast summary: gemma3:latest (3.1GB, instant)
Detailed summary: qwen2.5-14b:docs (8.4GB, 30sec)
Context pack: qwen3:8b (5.2GB, 10sec)
```

---

## Part 4: Maximum Concurrent Loads (Practical)

### With OLLAMA_NUM_PARALLEL=1 enforced:

```
TIER 1 models loaded: ∞ (negligible footprint)
TIER 2 models loaded: 1 (8-10GB RAM/VRAM)
TIER 3 models loaded: 1 (14-20GB RAM)
TIER 4 models loaded: 1 (32-40GB RAM)
TIER 5 models loaded: 1 (50-70GB RAM)

Practical Maximum Unique Active: 1 at any time
Practical Queued: 5-10 (with proper serialization)
```

### Example Queue Scenario:
```
QUEUE:
1. [TIER 5] qwen2.5-72b:escalation (running) - 50GB
2. [TIER 2] qwen3:8b (waiting)
3. [TIER 3] qwen2.5-14b:docs (waiting)
4. [TIER 4] qwen2.5-coder-32b:coding (waiting)
5. [TIER 1] nomic-embed-text (can run now, doesn't block)

EXECUTION ORDER:
1. Start TIER 5 (blocking)
2. Wait for TIER 5 completion
3. Unload TIER 5 (free 50GB)
4. Start TIER 4 (blocking others)
5. TIER 1 runs in parallel
```

---

## Part 5: Failure Modes & Recovery

### Scenario 1: "Tier 4 model requested while Tier 2 is active"

**What happens:**
1. Request queued
2. Tier 2 model waits up to 30min (keep-alive)
3. If still active after keep-alive: auto-unload
4. Tier 4 starts loading

**Recovery:** Automatic (no manual action)

---

### Scenario 2: "Tier 5 model hangs after 10 minutes"

**What happens:**
1. Timeout triggered (600 seconds = 10 min)
2. System cannot recover gracefully
3. Manual restart required

**Recovery procedure:**
```bash
# On Windows:
taskkill /IM ollama.exe /F

# Wait 30 seconds for cleanup
timeout 30

# Restart Ollama (via tray icon or:)
start "" "C:\Users\YvesT\AppData\Local\Programs\Ollama\ollama.exe"

# Wait for service ready (check every 5 sec)
:check_loop
curl -s http://localhost:11434/api/tags >nul
if %errorlevel% neq 0 timeout 5 && goto check_loop

# Verify status
curl http://localhost:11434/api/tags
```

---

### Scenario 3: "Request times out and memory is not freed"

**What happens:**
1. Inference request times out
2. Model unloaded from GPU
3. But RAM not fully released

**Recovery:**
```bash
# Force unload
curl -d '{"model":"model_name","keep_alive":"0"}' \
  http://localhost:11434/api/generate

# Verify freed
curl http://localhost:11434/api/ps  # Should show []
```

---

### Scenario 4: "Out of memory error on Tier 4 load"

**What happens:**
1. System has <20GB free RAM
2. Model load fails
3. Request rejected

**Recovery:**
```bash
# Option 1: Wait (garbage collection may free RAM)
# Option 2: Close other apps
# Option 3: Use lighter model (Tier 3 instead)
# Option 4: Restart system
```

---

## Part 6: Safeguard Procedures

### Pre-Load Checklist (For Tier 4+)

```
[ ] curl http://localhost:11434/api/ps → [] (no models active)
[ ] Check RAM: psutil or 'tasklist /v'
    - Tier 3: 16GB free minimum
    - Tier 4: 20GB free minimum
    - Tier 5: 25GB free minimum
[ ] Check VRAM: nvidia-smi
    - Minimum 5GB free
[ ] Set timeout handler (see below)
[ ] Start inference
```

### Timeout Handler Template (Python)

```python
import requests
import time
from threading import Thread

class ModelTimeout:
    def __init__(self, model_name, timeout_sec):
        self.model_name = model_name
        self.timeout_sec = timeout_sec
        self.started = time.time()

    def check(self):
        elapsed = time.time() - self.started
        if elapsed > self.timeout_sec:
            print(f"TIMEOUT: {self.model_name} exceeded {self.timeout_sec}s")
            # Kill inference gracefully
            requests.post("http://localhost:11434/api/stop")
            return False
        return True

# Usage:
timeout = ModelTimeout("qwen2.5-coder-32b:coding", timeout_sec=300)
while timeout.check():
    # Do inference
    time.sleep(1)
```

---

## Part 7: Configuration Summary

### Environment Variables to Set

```bash
# Non-negotiable (already set)
OLLAMA_NUM_PARALLEL=1
OLLAMA_MMAP=1
OLLAMA_GPU=1
GGML_CUDA_NO_PINNED=1

# Optional enhancements (recommended)
OLLAMA_KEEP_ALIVE=30m     # Keep small models ready
OLLAMA_FLASH_ATTENTION=1  # If GPU supports

# For WSL (if migrating)
OLLAMA_HOST=0.0.0.0:11434
OLLAMA_LOAD_TIMEOUT=120s
OLLAMA_NUM_THREADS=16     # Set to CPU core count
```

### Files to Monitor

```
GPU Status:     nvidia-smi (VRAM usage)
Model Status:   curl http://localhost:11434/api/ps
Model List:     curl http://localhost:11434/api/tags
Ollama Logs:    C:\Users\YvesT\AppData\Local\Ollama\logs
```

---

## Summary: The 3 Core Rules for Safe Operation

### Rule 1: Only 1 Tier 4+ Model at a Time
- OLLAMA_NUM_PARALLEL=1 enforces this
- Never try to load 2 large models in parallel
- Use serialization queue for workloads

### Rule 2: Check Resources Before Tier 4+
- Verify free RAM (20GB minimum)
- Verify free VRAM (5GB minimum)
- Reject request if guardrails violated

### Rule 3: Unload Tier 5 Immediately After Use
- Don't keep it resident
- Set keep_alive=0 for cleanup
- System is stable only with tier 5 unloaded

**Follow these 3 rules and the system will be safe and productive.**

---

**Phase 4 Status:** COMPLETE
**Next Phase:** Testing & validation (Phase 5)
