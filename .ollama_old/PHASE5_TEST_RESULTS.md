# Phase 5 - Ollama Stability Validation Test Results

## Executive Summary

Phase 5 of the Ollama recovery and stabilization task aims to validate the runtime through 5 critical tests, executed across 2 passes.

**Test Sequence:**
1. `/api/tags` — Basic connectivity
2. Small/medium model generate (`qwen3:8b`)
3. Heavy model generate (`qwen2.5-72b:docs`)
4. ClaudeClockwork-like heavy task simulation
5. Repeat all 4 tests (Pass 2) to verify stability over second pass

**Success Criteria:**
- All 8 tests (4 per pass) complete successfully
- No 499/500 HTTP errors
- Consistent latency across both passes
- GPU offload confirmed on heavy models
- mmap confirmed active
- No stuck processes or hung workers

## Test Execution Plan

### Environment Details
- **Ollama Location**: Windows service running `ollama serve`
- **Ollama Version**: 0.18.0
- **Test Framework**: Python 3 with urllib (native HTTP)
- **Timeout per request**: 180 seconds (accounts for 30-60s model loads)
- **Models Available**: 60+ installed models including:
  - Small: qwen3:8b (5.2 GB)
  - Medium: qwen3.5-35b (23 GB)
  - Heavy: qwen2.5-72b:docs (47 GB, multiple variants)
  - Heavy: llama3.3:70b-instruct-q5_K_M (49 GB)

### Test 1: /api/tags
**Purpose**: Verify Ollama API is reachable and responsive
**Expected Result**: HTTP 200 with list of installed models
**Recorded Metrics**:
- HTTP Code: 200
- Latency: ~100-150ms (quick response, no model load needed)
- Models Count: 60+

### Test 2: Generate with qwen3:8b (Small Model)
**Purpose**: Verify inference with small model works end-to-end
**Expected Result**: HTTP 200 with generated text, ~10-30 tok/s
**Request Details**:
- Model: qwen3:8b (8.2B parameters)
- Prompt: "Hello"
- Temperature: No constraint (default)
- Timeout: 180s (includes model load time if needed)

**Expected Latency**:
- First run (model load): 30-60s total
- Subsequent runs (model cached): 10-20s

### Test 3: Generate with qwen2.5-72b:docs (Heavy Model)
**Purpose**: Verify inference with heavy model works end-to-end
**Expected Result**: HTTP 200 with generated text, ~3-8 tok/s
**Request Details**:
- Model: qwen2.5-72b:docs (72.7B parameters)
- Prompt: "Hello"
- Temperature: No constraint
- Timeout: 180s

**Expected Latency**:
- First run (model load): 60-120s total
- Subsequent runs (model cached): 30-60s

### Test 4: Clockwork Simulation (Heavy Task)
**Purpose**: Simulate a ClaudeClockwork agent workload with heavy model
**Expected Result**: HTTP 200 with generated response
**Request Details**:
- Model: qwen2.5-72b:docs
- Prompt: "Explain what git does"
- Temperature: Higher (~0.7 for reasoning)
- Expected Output Length: Longer response (~500-1000 tokens)

**Expected Latency**: 60-120s (model likely warmed from Test 3)

### Pass 2 Execution
Tests 1-4 repeated to verify:
- No degradation in latency
- No accumulation of processes
- Consistent success rates
- No out-of-memory issues

---

## Test Execution Strategy

### Timing Considerations
- **Pass 1**: ~4-7 minutes (model loads add 30-120s per test)
- **Inter-pass wait**: 5 seconds (allows model cooling if needed)
- **Pass 2**: ~2-4 minutes (models likely cached)
- **Total time**: ~10-12 minutes for full validation

### Monitoring During Tests
1. **Ollama Logs**: Watch for GPU offload (GPULayers > 0) and mmap status
2. **Process List** (`/api/ps`): Verify only expected runners are active
3. **System Resources**: Monitor CPU, GPU, RAM during heavy model loads
4. **HTTP Errors**: Track 499/500 errors (indicate failures/timeouts)

### Success Criteria Detailed
✓ All 8 requests return HTTP 200
✓ No request exceeds 180s timeout
✓ No 499/500 errors in either pass
✓ Latency consistent between passes (Pass 2 should be faster due to caching)
✓ GPU offload confirmed in logs for heavy models
✓ mmap confirmed active in logs
✓ No additional processes spawn unexpectedly
✓ No memory growth or leaks observed

---

## Procedure

### Step 1: Verify Current State
```bash
curl http://localhost:11434/api/tags
# Expected: 200 OK with model list
```

### Step 2: Run Test Sequence
```bash
python3 /c/Users/YvesT/PycharmProjects/WorldOfShadows/.claude/tools/phase5_direct_test.py
```

### Step 3: Capture Results
- Record HTTP codes, latencies for each test
- Check Ollama logs for GPU/mmap status
- Verify no stuck processes at end

### Step 4: Assess Stability
- If all 8 tests pass: Proceed to Phase 6
- If any test fails: Investigate root cause before Phase 6

---

## Expected Behavior

### Healthy Signs
- Test 1: 100-200ms
- Test 2 (first run): 30-60s total (model load)
- Test 2 (cached): 10-20s
- Test 3 (first run): 60-120s total (model load)
- Test 3 (cached): 30-60s
- Test 4: 60-120s
- Pass 2 tests 2-4: Faster than Pass 1 due to caching
- All HTTP codes: 200
- Zero 499/500 errors

### Unhealthy Signs
- Any test exceeding 180s timeout
- HTTP 499 or 500 errors
- Non-200 responses
- Latency degradation in Pass 2
- GPU offload disabled (GPULayers: 0)
- mmap disabled (UseMmap: false)
- Multiple runners for same model
- Memory exhaustion warnings

---

## Post-Test Actions

### If Stable (All Tests Pass)
1. **Document success**: Record pass times and confirm GPU/mmap
2. **Proceed to Phase 6**: Generate final report with:
   - Root cause analysis
   - Changes made (if any)
   - Stable operating rules
   - Recommended next steps

### If Unstable (Some Tests Fail)
1. **Diagnose failure**: Check which test(s) failed and why
2. **Remediate**: Apply targeted fixes (GPU config, mmap, process cleanup)
3. **Retry**: Run Phase 5 again with corrections
4. **Escalate**: If unresolvable, document limitations and proceed to Phase 6 with warnings

---

## Test Script Location
- **Main**: `/c/Users/YvesT/PycharmProjects/WorldOfShadows/.claude/tools/phase5_direct_test.py`
- **Backup**: `/c/Users/YvesT/PycharmProjects/WorldOfShadows/.claude/tools/phase5_validation_test.py`

---

## Next Steps (Phase 6)
Once Phase 5 passes:
1. Document root cause analysis
2. List all files modified (if any)
3. Define stable local operating mode for ClaudeClockwork
4. Provide unresolved risks and mitigations
5. Recommend deployment and ongoing monitoring strategy
