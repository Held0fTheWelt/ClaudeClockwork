# Ollama Architecture and Resource Interactions

**Audience**: Infrastructure Architects, System Designers
**Date**: March 16, 2026
**Status**: Production-Ready

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     ClaudeClockwork                         │
│              (Agent Orchestration Layer)                    │
├─────────────────────────────────────────────────────────────┤
│  Requests:  [brief] [draft] [review] [architecture]         │
│  Model:     All → qwen2.5-72b:* (single-model mode)        │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
                          │ Port 11434
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    Ollama Service                           │
│              (Local LLM Model Server)                       │
├─────────────────────────────────────────────────────────────┤
│  API Layer:   /api/generate, /api/tags, /api/ps           │
│  Queue:       OLLAMA_NUM_PARALLEL=1 (serialized)           │
│  Keep-Alive:  OLLAMA_KEEP_ALIVE=5m                         │
│  Max Models:  OLLAMA_MAX_LOADED_MODELS=1                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ↓               ↓               ↓
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │   RAM    │  │  VRAM    │  │   GPU    │
    │  64 GB   │  │ 10 GB    │  │RTX 3080  │
    │(System)  │  │(NVIDIA)  │  │(10GB)    │
    └──────────┘  └──────────┘  └──────────┘
         │               │
         └───────┬───────┘
                 │
         ┌───────────────┐
         │   mmap File   │
         │  Paging Cache │
         └───────────────┘
```

---

## Memory Architecture

### System Memory Layout

```
64 GB Total System RAM
════════════════════════════════════════════════════

┌─ 5-8 GB     Windows OS + Kernel
├─ 8-10 GB    Background Applications
│             (VS Code, Chrome, etc.)
│
├─ Available: ~46-51 GB
│
├─ 40-42 GB   Ollama + qwen2.5-72b Model
│             ├─ Ollama Process Base: ~300 MB
│             ├─ Model Weights in RAM: ~40 GB
│             └─ Metadata & Buffers: ~200 MB
│
└─ 3-10 GB    Operating Margin
              (Buffer cache, variances)
```

### Model Memory Consumption

**qwen2.5-72b (72.7B parameters, Q5 quantization)**:

```
Model Size Breakdown:
═════════════════════════════════════════════

Storage (GGUF on disk): 47 GB
├─ Weights: 46.7 GB
└─ Metadata: 0.3 GB

In-Memory (when loaded): 40-42 GB
├─ Weights in RAM: 39-40 GB
├─ GPU VRAM (with gpu_layers=6): 2-3 GB
├─ Inference Buffers: 1-2 GB
└─ Metadata: 0.2 GB

Why the difference (47 GB disk → 42 GB RAM)?
- Quantization already applied (Q5 format)
- No further compression in memory
- Slight overhead from inference buffers
```

**Quantization Impact** (Q5 = 5-bit):

```
Original (float32): 72.7B * 4 bytes = ~291 GB (hypothetical)
Q5 Quantization: ~291 GB * (5/32) = ~45 GB
Actual on-disk: 47 GB
Actual in-RAM: 40-42 GB
```

### GPU/CPU Split with GPU Offloading

**RTX 3080 Configuration** (10GB VRAM):

```
OLLAMA_GPU_LAYERS=6  (Conservative offload)
═════════════════════════════════════════════

Model Layer Distribution:
┌─ GPU VRAM (RTX 3080, 10GB)
│  ├─ 6 model layers: ~2-3 GB
│  ├─ Inference buffers: ~1-2 GB
│  ├─ CUDA kernels: ~0.5 GB
│  └─ Free VRAM: 4-5 GB
│
└─ System RAM
   ├─ Remaining model layers: 39-40 GB
   ├─ mmap cache: ~1-2 GB (shared with disk)
   └─ I/O buffers: 0.5-1 GB
```

**Performance Characteristics**:

```
Inference Token Generation:

Layer Access Pattern:
  GPU Layers (6):     Access time ~100 ns (from VRAM)
  RAM Layers:         Access time ~500 ns (from RAM)
  Paged (swap):       Access time ~5-10 ms (from disk)

Token Speed:
  All in GPU:         Impossible (model too large)
  GPU + RAM:          2-4 tok/s (current config)
  GPU + RAM + Paging: 0.1 tok/s (stuck, timeout risk)
```

---

## Request Processing Flow

### Single Request Lifecycle

```
Request Arrives
│ (e.g., POST /api/generate)
│
├─ Step 1: Queue Check
│  └─ OLLAMA_NUM_PARALLEL=1 enforces serialization
│     If inference in progress: Wait
│     If queue > 1: Additional wait
│
├─ Step 2: Model Load Check
│  ├─ Is qwen2.5-72b already in memory?
│  │  ├─ YES: Skip to Step 4
│  │  └─ NO: Load from disk
│  │
│  └─ Step 3: Load Model from Disk
│     ├─ Load GGUF file: 47 GB → 40 GB RAM
│     ├─ Initialize GPU offload: 2-3 GB VRAM
│     ├─ Prepare buffers: 1-2 GB
│     └─ Time: 55-65 seconds
│
├─ Step 4: Execute Inference
│  ├─ Process input tokens
│  ├─ Run model forward pass (token by token)
│  ├─ Speed: 2-4 tok/s (depends on context length)
│  └─ Time: Depends on output length
│
├─ Step 5: Return Response
│  ├─ Send HTTP 200 OK
│  ├─ Include generated text
│  └─ Update timestamp (for keep-alive)
│
└─ Step 6: Keep-Alive Timer Reset
   ├─ Model remains in memory
   ├─ Timer: 5 minutes (OLLAMA_KEEP_ALIVE=5m)
   ├─ After 5 min inactivity: Model unloaded
   └─ Next request: Reload cycle starts again
```

### Concurrent Request Handling

**With OLLAMA_NUM_PARALLEL=1**:

```
Time    Request 1          Request 2          Request 3
───────────────────────────────────────────────────────────
00:00   Load model (55s)   [Waiting]          [Waiting]
00:55   Inference (30s)    [Waiting]          [Waiting]
01:25   Complete           Load model (55s)   [Waiting]
02:20                      Inference (45s)    [Waiting]
03:05                      Complete           Load model (55s)
04:00                                         Inference (30s)
04:30                                         Complete

Total time for 3 requests: 4.5 minutes (serialized)
If parallel (without limit): ~2 minutes (but would cause OOM)
```

---

## Keep-Alive Mechanism

### Model Lifecycle with Keep-Alive

```
Request 1 Completes (01:30)
│
├─ Model kept in RAM: 40-42 GB
├─ Keep-alive timer starts: 5 minutes
├─ No new requests for 4 minutes
│
├─ New Request arrives (05:20)
│  └─ Model still in RAM (timer reset)
│     └─ Inference starts immediately (no reload)
│
├─ Request 2 completes (05:50)
├─ Keep-alive timer resets: 5 minutes
├─ No requests for 6 minutes (expires after 5)
│
└─ Timer expires at 10:50
   ├─ Model unloaded (40-42 GB freed)
   ├─ RAM available again
   └─ Next request must reload (55s delay)
```

### Why Keep-Alive is Necessary

**Without keep-alive** (model always unloads):
- After each request: Unload immediately
- Next request: Wait 55s for reload
- Throughput: ~5-10 requests/hour

**With keep-alive** (model stays loaded):
- Requests within 5 min: No reload time
- Throughput: ~30-60 requests/hour (5x improvement)

**Tradeoff**: Memory stays allocated 5 minutes longer

---

## Resource Contention and Failure Modes

### Failure Mode 1: Memory Exhaustion (Phase 5 Observed)

**Scenario**: Multiple large models loaded simultaneously

```
Timeline:
─────────────────────────────────────────────
T=0:    Request for qwen2.5-72b
        └─ Start loading 47 GB from disk

T=60:   Model loaded, using 40-42 GB RAM
        └─ Keep-alive starts

T=120:  New request for qwen3:8b (5.2 GB)
        └─ qwen2.5-72b still in RAM (keep-alive not expired)

T=122:  Attempt to allocate 5.2 GB for qwen3:8b
        ├─ Free RAM available: 5-10 GB
        ├─ Total needed: 42 GB + 5.2 GB = 47.2 GB
        └─ Available: 64 GB
              - OS: 5-8 GB
              - Existing model: 42 GB
              - Free: ~14-17 GB (enough theoretically)

T=125:  Model load attempts allocation
        └─ But contiguous block needed
        └─ Fragmentation: RAM split into chunks
        └─ Largest contiguous block: ~8 GB (insufficient)

T=126+: System resorts to disk paging
        ├─ Swap pages 1-2 GB to disk
        ├─ Latency jumps from 500ns to 5ms (10,000x slower)
        ├─ Inference times out (180s exceeded)
        └─ Request fails with HTTP timeout
```

**Root Cause**: Memory fragmentation + contiguous allocation failure

**Prevention**: Single-model mode (only 1 model at a time)

### Failure Mode 2: Runaway Memory Leak

**Scenario**: Memory gradually increases over hours

```
Hour    Memory Usage    Status
────────────────────────────────────
 1      15 GB          5 requests processed
 2      18 GB          5 requests processed
 3      22 GB          5 requests processed
 4      27 GB          5 requests processed
 5      32 GB          5 requests processed
 6      38 GB          [WARNING] Memory > 35GB
 7      42 GB          [CRITICAL] Auto-restart

Likely Cause:
└─ Ollama process not cleaning up buffers
└─ Each inference leaves ~1GB residual
└─ After 40 inferences: ~40GB leak
```

**Prevention**:
1. Daily restart at 02:00 AM (clears all memory)
2. Memory monitoring with auto-restart @ 40GB
3. Update Ollama if bug is discovered

### Failure Mode 3: GPU Driver Hang

**Scenario**: GPU becomes unresponsive

```
Symptoms:
├─ Ollama process: High CPU (100%), not responding
├─ GPU (nvidia-smi): Frozen, no output
├─ System: Still responsive, but Ollama stuck

Cause:
├─ GPU driver deadlock
├─ CUDA kernel infinite loop
└─ Rare, but possible with certain model/driver combos

Recovery:
├─ Kill Ollama process: pkill -9 ollama
├─ Restart GPU driver: systemctl restart nvidia-persistenced
├─ Restart Ollama: systemctl start ollama
```

**Prevention**: Use tested driver versions, monitor GPU health

---

## Performance Characteristics

### Latency Breakdown

**First Request** (model not loaded):
```
Total Time: 70-80 seconds
├─ Model load from disk: 55-60 seconds (I/O bound)
├─ Model initialization: 2-3 seconds
├─ First token generation: 2-5 seconds
└─ Response transmission: < 1 second
```

**Subsequent Request** (model loaded, within 5 min):
```
Total Time: 30-50 seconds
├─ Inference only: 30-50 seconds
├─ Token generation rate: 2-4 tok/s
├─ For 100 tokens: ~25 seconds
├─ For 1000 tokens: ~250 seconds (timeout risk)
└─ Keep-alive timer reset: < 1 second
```

### Throughput Estimates

**Single Ollama Instance, Single-Model Mode**:

```
Request Type                Time        Requests/Hour
──────────────────────────────────────────────────
Simple (100 tokens)         60s         ~1.0 req/min = 60/hr
Medium (500 tokens)         90s         ~0.67 req/min = 40/hr
Complex (1000 tokens)       150s        ~0.4 req/min = 24/hr
Average Mix (500 tokens)    ~80s        ~0.75 req/min = 45/hr
```

**Bottleneck Analysis**:
- Compute: 20% (token generation)
- I/O: 70% (model loading, disk cache)
- Memory: 10% (contention, if any)

---

## Scaling Architecture

### Current: Single Instance

```
Load Balancer (N/A)
        │
        ↓
   Ollama (Port 11434)
   ├─ Memory: 40-42 GB (qwen2.5-72b)
   ├─ GPU: RTX 3080 (offload 6 layers)
   ├─ Throughput: 45 req/hr average
   └─ Cost: 1 machine
```

### Horizontal Scaling Option 1: Multiple Instances on Same Machine

```
Not feasible with current 64GB RAM:
├─ Instance 1: 40-42 GB (qwen2.5-72b)
├─ Instance 2: Would need 40-42 GB
├─ Total: 80-84 GB (exceeds 64GB)

Requires: 128GB+ system RAM
```

### Horizontal Scaling Option 2: Multiple Machines

```
Machine 1               Machine 2
  Ollama 1              Ollama 2
  qwen2.5-72b         qwen2.5-72b
  45 req/hr           45 req/hr
       │                  │
       └──────┬───────────┘
              │
        Load Balancer
              │
         ClaudeClockwork
              │
        Total: 90 req/hr
```

**Load Balancer Configuration**:
```
Upstream ollama_1 {
    server 192.168.1.10:11434;
}

Upstream ollama_2 {
    server 192.168.1.11:11434;
}

Location /api/ {
    proxy_pass http://ollama_1;
    # Fallback to ollama_2 if ollama_1 fails
}
```

### Horizontal Scaling Option 3: Model Diversity

**Requires**: 128+ GB RAM, dedicated single-model instances

```
Machine 1: qwen2.5-72b:coding (40GB)
Machine 2: qwen2.5-14b:docs (8GB)
Machine 3: qwen2.5-14b:review (8GB)

Router:
├─ Task: "code_review" → Machine 2 or 3
├─ Task: "code_generation" → Machine 1
├─ Task: "architecture" → Machine 1
└─ Task: "documentation" → Machine 2

Benefits:
├─ Model diversity available
├─ Task-specific optimization
└─ Higher total throughput
```

---

## Resource Monitoring Points

### Critical Metrics

**Memory Usage** (Most Important):
```bash
# Query every 30 seconds
tasklist | grep ollama | awk '{print $NF}'

# Alert thresholds:
# 35GB: WARNING (slow response expected)
# 40GB: CRITICAL (auto-restart)
# >42GB: SYSTEM ERROR (possible leak)
```

**API Latency**:
```bash
# Query every 5 minutes
time curl http://localhost:11434/api/tags

# Alert thresholds:
# 200ms: NORMAL
# 500ms: SLOW (system busy)
# 1000ms+: DEGRADED (investigate)
```

**Process Health**:
```bash
# Query every minute
ps aux | grep ollama | grep -v grep

# Alert thresholds:
# CPU >80% for >5 min: Investigate (possibly stuck)
# Memory growth >1GB/hour: Possible leak
# Process count !=3-5: Zombie processes
```

---

## System Design Principles

### Why Single-Model Mode

**Principle**: Constraint system to operate within tested boundaries

```
Multi-Model Attempt:
├─ Goal: Optimize for different task types
├─ Theory: Small models for docs, large for code
├─ Reality: Memory contention, unpredictable
├─ Result: 50% failure rate (Phase 5)

Single-Model Solution:
├─ Goal: 100% reliability
├─ Theory: Eliminate model competition
├─ Reality: Simple, predictable, stable
├─ Result: 100% success rate (Phase 6)
```

### Principle: Fail Fast, Recover Automatically

```
Detected Issue           Automatic Action       Time to Recover
──────────────────────────────────────────────────────────────
Memory > 40GB            Auto-restart           ~10 seconds
API timeout              Alert ops              ~5 minutes manual
Process hung             Monitor + alert        ~15 minutes manual
Nightly:                 Scheduled restart      ~5 minutes scheduled
```

### Principle: Observability > Optimization

```
Better to be slow and predictable:
├─ Latency: 60-150 seconds/task (known)
├─ Memory: 40-42 GB (stable)
├─ Errors: 0% (in single-model mode)

Than fast and unpredictable:
├─ Latency: 30-180 seconds (erratic)
├─ Memory: 15-42 GB (variable)
├─ Errors: 10-50% (timeouts)
```

---

## Cost-Benefit Analysis

### Current Architecture Cost

```
Hardware:
├─ CPU: Moderate (inference is GPU-bound)
├─ RAM: High (64GB required for qwen2.5-72b)
├─ GPU: High (RTX 3080, 10GB VRAM)
└─ Total: ~$3,000 - $4,000 one-time

Operational:
├─ Power: ~200-300W sustained
├─ Cooling: Included (standard datacenter)
├─ Monitoring: 2-4 hours/month ops team
└─ Total: ~$100-150/month

Throughput:
├─ 45 requests/hour average
├─ 1,080 requests/day
├─ 32,400 requests/month
├─ Cost per request: ~$0.003-0.005 (amortized)
```

### Scaling Cost

```
To 2x throughput (90 req/hr):
├─ Add 1 more machine: +$3,000
├─ Power: +$150/month
├─ Total cost: doubles

To 10x throughput (450 req/hr):
├─ Add 9 more machines: +$27,000
├─ Power: +$1,500/month
├─ Need load balancer: +$2,000
├─ Ops overhead: +50 hours/month
└─ Much more cost-effective than using Claude API at scale
```

---

## Conclusion

Ollama provides a cost-effective local LLM server with predictable resource consumption when properly configured with single-model mode constraint. The architecture is stable, monitorable, and scalable through replication.

**Key Design Takeaway**: Constraint + Automation = Reliability

---

**Document Status**: Production-Ready
**Last Updated**: 2026-03-16 17:00 UTC
**Audience**: Architecture, Infrastructure, Engineering Leadership

