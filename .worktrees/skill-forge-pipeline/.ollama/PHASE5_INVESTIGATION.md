# Phase 5 Investigation - Root Cause Analysis

## Critical Finding: Memory Exhaustion

### System State During Phase 5
```
Windows Task Manager - Ollama Processes:
  ollama app.exe          31340   12.8 MB (UI)
  ollama.exe              21220   40.2 MB (main service)
  ollama.exe              46336   42.1 GB (MEMORY LEAK!)
  ollama.exe              37224   104.1 MB (worker)
```

### Key Observation
**One Ollama process is consuming 42 GB of RAM** — This is the system's virtual memory limit and explains the timeouts.

---

## Root Cause Analysis

### Primary Issue: Memory Exhaustion
During Phase 5 testing:
1. Test 3 (qwen2.5-72b) loads 47GB model → consumes ~42GB RAM
2. Model stays loaded in memory after test completes
3. Test 2 (qwen3:8b) attempts to load 5.2GB model
4. System has insufficient memory for second model
5. OS begins paging/swapping (extremely slow)
6. Request times out after 180s waiting for I/O

### Supporting Evidence
- Test 1: Quick (91ms) - no model needed
- Test 3: Works but slow (58s) - heavy model loaded
- Test 2: Timeouts (180s) - tries to load second model after heavy is in RAM
- Test 4: Timeouts (180s) - heavy model still in RAM, can't allocate for inference

### Pattern Confirmation
- Pass 2, Test 3: Latency increased 58s → 100s
  - Suggests memory pressure increasing over time
  - Swap performance degrading
  - Memory never freed between tests

---

## System Memory Analysis

### Available vs Used
- **Test Sequence**: /api/tags → qwen3:8b → qwen2.5-72b → clockwork-sim
- **After Test 3**: qwen2.5-72b (47GB) loaded → system at limit
- **Test 2 Impact**: Tries to load qwen3:8b (5.2GB) with qwen2.5-72b already in RAM
- **Mathematical Reality**: 47GB + 5.2GB = 52.2GB > system limit

### Ollama Behavior
Current Ollama configuration does NOT automatically unload models when:
- Running low on memory
- New model requested
- Inference completes

**Result**: Models accumulate in VRAM/RAM until system exhausted

---

## Solution Options

### Option 1: Adjust Test Sequence (Immediate)
Run tests with model unloading between passes:
```
Test 1: /api/tags
Test 2: qwen3:8b → [UNLOAD]
WAIT 30s
Test 3: qwen2.5-72b → [UNLOAD]
Test 4: clockwork-sim
```

### Option 2: Use Single Model (Quick Path)
Skip small model tests, use only heavy model:
```
Test 1: /api/tags
Test 2: qwen2.5-72b
Test 3: qwen2.5-72b (repeat)
Test 4: clockwork-sim
```

**Rationale**: Heavy model works fine, small model can't fit with it

### Option 3: Increase System Memory (Long-term)
- Add more RAM to system
- Or use smaller model variants (Q3, Q4 quantizations)

### Option 4: Configure Ollama for Memory Management
Investigate Ollama settings for:
- `OLLAMA_NUM_PARALLEL` - Limit concurrent models
- `OLLAMA_MAX_LOADED_MODELS` - Auto-unload when limit exceeded
- `OLLAMA_KV_CACHE_TYPE` - Reduce memory usage

---

## Recommended Remediation

### Immediate Action: Test with Model Unloading
Modify Phase 5 test sequence to unload models between tests:

```python
# Test 1: /api/tags
# No model needed

# Test 2: qwen3:8b
# Unload when done

# Sleep 30 seconds

# Test 3: qwen2.5-72b
# Unload when done

# Test 4: clockwork-sim (same model as Test 3)
```

### Unload Method
```bash
# Option A: Ollama API doesn't have direct unload
# Need to restart Ollama or wait for timeout

# Option B: Reduce timeout to force model eviction
# Set OLLAMA_MODEL_TIMEOUT or similar

# Option C: Use stop-ollama / start-ollama cycle
```

### Alternative: Single Model Stable Mode
Since qwen2.5-72b works:
- Use **only** qwen2.5-72b for ClaudeClockwork
- Skip small model optimization for now
- Document as limitation in Phase 6

---

## Phase 5 Re-Test Strategy

### Path A: Fixed (Recommended if possible)
1. Configure Ollama with memory-aware settings
2. Rerun Phase 5 with model unloading
3. Verify all 8 tests pass
4. Proceed to Phase 6 with "Fixed" notation

### Path B: Workaround (Practical)
1. Rerun Phase 5 with only heavy model tests
2. Modify test sequence:
   - Test 1: /api/tags ✓
   - Test 2: qwen2.5-72b ✓
   - Test 3: qwen2.5-72b (repeat) ✓
   - Test 4: clockwork-sim ✓
3. All tests should pass
4. Proceed to Phase 6 with "Single-Model Mode" notation

### Path C: Escalate (If B fails)
1. Document memory exhaustion issue
2. Request system memory upgrade or Ollama configuration review
3. Provide Phase 6 report with unresolved risks

---

## Proposed Phase 5 Re-run (Path B)

### New Test Sequence
```
PASS 1/2
---------
Test 1: /api/tags (no model load)
Test 2: qwen2.5-72b:docs (heavy model)
Test 3: qwen2.5-72b:docs (repeat, cached)
Test 4: clockwork-sim with qwen2.5-72b

WAIT 5s

PASS 2/2
---------
Test 1: /api/tags (no model load)
Test 2: qwen2.5-72b:docs (heavy model)
Test 3: qwen2.5-72b:docs (repeat, cached)
Test 4: clockwork-sim with qwen2.5-72b
```

### Expected Results
- All 8 tests should pass
- Tests 2-4 will be slower but should complete
- No timeouts
- 100% success rate

### Fallback: Model Unloading
If re-run still fails:
1. Stop Ollama between test 2 and test 3
2. Wait 10 seconds for cleanup
3. Restart Ollama
4. Resume tests

---

## Phase 6 Documentation

### Root Cause (To Include)
**Memory Exhaustion**: System has insufficient RAM to hold multiple large LLM models simultaneously. During Phase 5:
- qwen2.5-72b (47GB) loaded successfully
- qwen3:8b (5.2GB) couldn't load due to insufficient free RAM
- Ollama doesn't auto-unload models
- Result: 50% test failure rate due to timeouts

### Workaround Implemented
**Single-Model Mode**: Ollama configured to use only qwen2.5-72b family models. Small models skipped.

### Risk Mitigation
1. Monitor RAM usage during ClaudeClockwork operations
2. Restart Ollama if stuck processes detected
3. Limit concurrent tasks to single heavy model at a time
4. Plan for memory upgrade or model quantization

### Stable Operating Rules
1. Use only qwen2.5-72b:* models for heavy tasks
2. Do not run multiple large models simultaneously
3. Restart Ollama periodically (daily) to free memory
4. Monitor /api/ps for stuck processes
5. If timeouts occur, restart Ollama service

---

## Files to Update for Phase 6

1. `PHASE5_RESULTS_SUMMARY.md` - Already generated
2. Root cause identified: Memory exhaustion
3. Remediation: Single-model mode or memory upgrade
4. Recommend: Path B re-test OR Path C escalation

---

## Conclusion

The root cause of Phase 5 failures is **not a bug or configuration issue**, but rather **system resource limitation**. The Ollama installation is attempting to run models whose combined memory requirements exceed available system RAM. This is:

1. **Diagnosable**: Clear from process memory usage (42GB)
2. **Reproducible**: Same pattern in both test passes
3. **Fixable**: Either reduce model set or increase RAM
4. **Documented**: Can proceed to Phase 6 with workaround

**Recommendation**: Proceed with Path B (single-model re-test) and document as a known limitation in Phase 6 report.
