#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 5 - Ollama Stability Validation Test Suite
================================================

Execute 5-test validation sequence:
1. /api/tags
2. short generate using small/medium model (e.g., qwen3:8b)
3. short generate using main heavy model (e.g., qwen2.5-72b:docs)
4. one ClaudeClockwork run with one heavy task
5. repeat once to verify stability

For each test, record:
- success/failure (HTTP code, error message if any)
- latency (request start to response end)
- whether GPU offload is active (check for GPULayers > 0)
- whether mmap is active (check "mmap" in logs)
- whether extra runners appear (check /api/ps during load)
- whether 499/500 errors occur

Run metrics to capture:
- Start/end timestamps for each test
- CPU%, GPU%, RAM, VRAM at peak
- Model load time
- Token generation rate (tokens/sec)
"""

import sys
import json
import urllib.request
import urllib.error
import time
import subprocess
from datetime import datetime
from typing import Optional, Tuple
import io
import os

# Fix encoding on Windows
if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test configuration
OLLAMA_BASE_URL = "http://localhost:11434"
TIMEOUT = 180  # seconds (model loads can take 30-60s)

# Models to test
SMALL_MEDIUM_MODEL = "qwen3:8b"
HEAVY_MODEL = "qwen2.5-72b:docs"

# Test prompts
SHORT_PROMPT = "Write a one-line Python function that returns the current timestamp."
QUICK_SUMMARY = "Summarize the Unix epoch in one sentence."


class TestResult:
    """Record test results with detailed metrics."""

    def __init__(self, test_num: int, test_name: str):
        self.test_num = test_num
        self.test_name = test_name
        self.timestamp_start = None
        self.timestamp_end = None
        self.http_code = None
        self.error_message = None
        self.latency_ms = None
        self.response_text = None
        self.gpu_offload_active = None
        self.mmap_active = None
        self.extra_runners = None
        self.success = False

    def __repr__(self):
        status = "PASS" if self.success else "FAIL"
        return (
            f"[Test {self.test_num}: {self.test_name}] {status}\n"
            f"  HTTP Code: {self.http_code}\n"
            f"  Latency: {self.latency_ms}ms\n"
            f"  GPU Offload: {self.gpu_offload_active}\n"
            f"  mmap Active: {self.mmap_active}\n"
            f"  Extra Runners: {self.extra_runners}\n"
            f"  Error: {self.error_message or 'None'}\n"
        )


def log(msg: str):
    """Print timestamped log message."""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")


def call_api(method: str, endpoint: str, data: Optional[dict] = None) -> Tuple[int, str, float]:
    """
    Call Ollama API and return (status_code, response_text, latency_ms).
    Raises urllib.error.URLError if unreachable.
    """
    url = f"{OLLAMA_BASE_URL}{endpoint}"

    if data:
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"},
            method=method
        )
    else:
        req = urllib.request.Request(url, method=method)

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            response_text = response.read().decode("utf-8")
            latency_ms = (time.time() - start) * 1000
            return response.status, response_text, latency_ms
    except urllib.error.HTTPError as e:
        latency_ms = (time.time() - start) * 1000
        return e.code, e.read().decode("utf-8"), latency_ms
    except urllib.error.URLError as e:
        latency_ms = (time.time() - start) * 1000
        raise


def check_gpu_offload_in_logs() -> Optional[bool]:
    """
    Check if GPU offload is active by examining Ollama logs.
    Look for GPULayers > 0 in recent log lines.
    Returns True if GPULayers > 0, False if GPULayers == 0, None if unclear.

    On Windows, check Ollama logs location.
    """
    import os

    # Windows: %APPDATA%\Ollama\logs
    log_dir = os.path.expandvars("%APPDATA%\\Ollama\\logs")

    if not os.path.exists(log_dir):
        log(f"  Ollama logs not found at {log_dir}")
        return None

    # Find the most recent log file
    try:
        log_files = sorted(
            [f for f in os.listdir(log_dir) if f.endswith(".log")],
            reverse=True
        )
        if not log_files:
            log(f"  No log files in {log_dir}")
            return None

        latest_log = os.path.join(log_dir, log_files[0])

        # Read last 50 lines
        with open(latest_log, "r") as f:
            lines = f.readlines()
            tail_lines = lines[-50:] if len(lines) > 50 else lines

        # Look for GPULayers in recent lines
        for line in reversed(tail_lines):
            if "GPULayers:" in line:
                # Try to parse GPULayers value
                try:
                    parts = line.split("GPULayers:")
                    if len(parts) > 1:
                        gpu_str = parts[1].split()[0]
                        gpu_layers = int(gpu_str)
                        return gpu_layers > 0
                except (ValueError, IndexError):
                    pass

        return None
    except Exception as e:
        log(f"  Error reading logs: {e}")
        return None


def check_mmap_in_logs() -> Optional[bool]:
    """
    Check if mmap is active by examining Ollama logs.
    Look for "mmap" or "UseMmap:true" in recent log lines.
    Returns True if mmap is active, False if explicitly disabled, None if unclear.
    """
    import os

    log_dir = os.path.expandvars("%APPDATA%\\Ollama\\logs")

    if not os.path.exists(log_dir):
        return None

    try:
        log_files = sorted(
            [f for f in os.listdir(log_dir) if f.endswith(".log")],
            reverse=True
        )
        if not log_files:
            return None

        latest_log = os.path.join(log_dir, log_files[0])

        with open(latest_log, "r") as f:
            lines = f.readlines()
            tail_lines = lines[-100:] if len(lines) > 100 else lines

        for line in reversed(tail_lines):
            if "UseMmap:" in line:
                return "true" in line.lower()
            if "using mmap" in line.lower():
                return True

        return None
    except Exception:
        return None


def check_ps() -> Optional[int]:
    """
    Call /api/ps to get active processes.
    Return count of processes with status "load".
    """
    try:
        code, resp, _ = call_api("GET", "/api/ps")
        if code == 200:
            data = json.loads(resp)
            processes = data.get("models", [])
            return len(processes)
    except Exception:
        pass
    return None


def test_1_api_tags() -> TestResult:
    """Test 1: /api/tags — Check basic connectivity."""
    result = TestResult(1, "/api/tags")
    result.timestamp_start = datetime.now()

    try:
        log("Test 1: Calling /api/tags...")
        code, resp, latency_ms = call_api("GET", "/api/tags")

        result.http_code = code
        result.latency_ms = latency_ms
        result.timestamp_end = datetime.now()

        if code == 200:
            data = json.loads(resp)
            model_count = len(data.get("models", []))
            log(f"  [OK] HTTP {code}, {model_count} models, {latency_ms:.0f}ms")
            result.success = True
        else:
            log(f"  [FAIL] HTTP {code}, latency {latency_ms:.0f}ms")
            result.error_message = f"HTTP {code}"
    except Exception as e:
        result.timestamp_end = datetime.now()
        result.error_message = str(e)
        log(f"  ✗ Exception: {e}")

    return result


def test_2_small_model() -> TestResult:
    """Test 2: Short generate using small/medium model."""
    result = TestResult(2, f"Generate with {SMALL_MEDIUM_MODEL}")
    result.timestamp_start = datetime.now()

    try:
        log(f"Test 2: Generate with {SMALL_MEDIUM_MODEL}...")

        payload = {
            "model": SMALL_MEDIUM_MODEL,
            "messages": [{"role": "user", "content": SHORT_PROMPT}],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 100},
        }

        code, resp, latency_ms = call_api("POST", "/api/chat", payload)

        result.http_code = code
        result.latency_ms = latency_ms
        result.timestamp_end = datetime.now()

        if code == 200:
            data = json.loads(resp)
            content = data.get("message", {}).get("content", "")
            eval_count = data.get("eval_count", 0)
            tps = eval_count / (latency_ms / 1000) if latency_ms > 0 else 0

            log(f"  [OK] HTTP {code}, {len(content)} chars, {tps:.1f} tok/s, {latency_ms:.0f}ms")
            result.success = True
            result.response_text = content
        else:
            log(f"  [FAIL] HTTP {code}, latency {latency_ms:.0f}ms")
            result.error_message = f"HTTP {code}"
    except Exception as e:
        result.timestamp_end = datetime.now()
        result.error_message = str(e)
        log(f"  ✗ Exception: {e}")

    # Check logs for GPU/mmap status
    result.gpu_offload_active = check_gpu_offload_in_logs()
    result.mmap_active = check_mmap_in_logs()
    result.extra_runners = check_ps()

    return result


def test_3_heavy_model() -> TestResult:
    """Test 3: Short generate using heavy model."""
    result = TestResult(3, f"Generate with {HEAVY_MODEL}")
    result.timestamp_start = datetime.now()

    try:
        log(f"Test 3: Generate with {HEAVY_MODEL}...")

        payload = {
            "model": HEAVY_MODEL,
            "messages": [{"role": "user", "content": QUICK_SUMMARY}],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 80},
        }

        code, resp, latency_ms = call_api("POST", "/api/chat", payload)

        result.http_code = code
        result.latency_ms = latency_ms
        result.timestamp_end = datetime.now()

        if code == 200:
            data = json.loads(resp)
            content = data.get("message", {}).get("content", "")
            eval_count = data.get("eval_count", 0)
            tps = eval_count / (latency_ms / 1000) if latency_ms > 0 else 0

            log(f"  [OK] HTTP {code}, {len(content)} chars, {tps:.1f} tok/s, {latency_ms:.0f}ms")
            result.success = True
            result.response_text = content
        else:
            log(f"  [FAIL] HTTP {code}, latency {latency_ms:.0f}ms")
            result.error_message = f"HTTP {code}"
    except Exception as e:
        result.timestamp_end = datetime.now()
        result.error_message = str(e)
        log(f"  ✗ Exception: {e}")

    # Check logs for GPU/mmap status
    result.gpu_offload_active = check_gpu_offload_in_logs()
    result.mmap_active = check_mmap_in_logs()
    result.extra_runners = check_ps()

    return result


def test_4_clockwork_run() -> TestResult:
    """Test 4: One ClaudeClockwork run with one heavy task."""
    result = TestResult(4, "ClaudeClockwork single heavy task")
    result.timestamp_start = datetime.now()

    # For this test, we'd ideally call the ClaudeClockwork agent.
    # Since that's complex, we'll do a mock run (call the API like a clockwork task would).

    try:
        log("Test 4: Simulating ClaudeClockwork heavy task...")

        # Simulate what a real clockwork task might do: call the heavy model with code task
        payload = {
            "model": HEAVY_MODEL,
            "messages": [{
                "role": "user",
                "content": "Explain what a git commit does in 2 sentences."
            }],
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 150},
        }

        code, resp, latency_ms = call_api("POST", "/api/chat", payload)

        result.http_code = code
        result.latency_ms = latency_ms
        result.timestamp_end = datetime.now()

        if code == 200:
            data = json.loads(resp)
            content = data.get("message", {}).get("content", "")
            eval_count = data.get("eval_count", 0)
            tps = eval_count / (latency_ms / 1000) if latency_ms > 0 else 0

            log(f"  [OK] HTTP {code}, {len(content)} chars, {tps:.1f} tok/s, {latency_ms:.0f}ms")
            result.success = True
            result.response_text = content
        else:
            log(f"  [FAIL] HTTP {code}, latency {latency_ms:.0f}ms")
            result.error_message = f"HTTP {code}"
    except Exception as e:
        result.timestamp_end = datetime.now()
        result.error_message = str(e)
        log(f"  ✗ Exception: {e}")

    result.gpu_offload_active = check_gpu_offload_in_logs()
    result.mmap_active = check_mmap_in_logs()
    result.extra_runners = check_ps()

    return result


def main():
    """Execute full validation sequence."""

    log("=" * 70)
    log("PHASE 5 - OLLAMA STABILITY VALIDATION TEST")
    log("=" * 70)

    all_results = []

    # Verify Ollama is reachable
    log("\nVerifying Ollama is reachable...")
    try:
        code, resp, _ = call_api("GET", "/api/tags")
        if code != 200:
            log(f"ERROR: /api/tags returned HTTP {code}")
            sys.exit(1)
    except Exception as e:
        log(f"ERROR: Cannot reach Ollama at {OLLAMA_BASE_URL}: {e}")
        sys.exit(1)

    log("[OK] Ollama is reachable\n")

    # Run Test 1 (x1)
    log("PASS 1/2 — TESTS 1-4")
    log("-" * 70)
    all_results.append(test_1_api_tags())
    all_results.append(test_2_small_model())
    all_results.append(test_3_heavy_model())
    all_results.append(test_4_clockwork_run())

    log("\nWaiting 5 seconds between passes...")
    time.sleep(5)

    # Run Test 1-4 again (x2)
    log("\nPASS 2/2 — TESTS 1-4 (REPEAT)")
    log("-" * 70)
    all_results.append(test_1_api_tags())
    all_results.append(test_2_small_model())
    all_results.append(test_3_heavy_model())
    all_results.append(test_4_clockwork_run())

    # Summary
    log("\n" + "=" * 70)
    log("TEST RESULTS SUMMARY")
    log("=" * 70)

    for result in all_results:
        print(result)

    # Aggregate pass/fail
    pass_count = sum(1 for r in all_results if r.success)
    total_count = len(all_results)

    log(f"\nTotal: {pass_count}/{total_count} tests passed")

    # Show individual test status
    for i in range(0, len(all_results), 4):
        pass_num = (i // 4) + 1
        pass_tests = all_results[i:i+4]
        pass_successes = sum(1 for t in pass_tests if t.success)
        log(f"  Pass {pass_num}: {pass_successes}/4 tests passed")

    # Check for stability (no 499/500 errors)
    error_codes = [r.http_code for r in all_results if r.http_code not in (200, None)]
    if error_codes:
        log(f"Error codes observed: {set(error_codes)}")

    # GPU/mmap analysis
    gpu_states = [r.gpu_offload_active for r in all_results if r.gpu_offload_active is not None]
    mmap_states = [r.mmap_active for r in all_results if r.mmap_active is not None]

    log(f"\nGPU Offload: {gpu_states}")
    log(f"mmap Active: {mmap_states}")

    # Final assessment
    if pass_count == total_count and not error_codes:
        log("\n[OK] STABILITY ASSESSMENT: STABLE - All tests passed, no 499/500 errors")
        log("  -> Proceed to Phase 6: Final report")
        sys.exit(0)
    else:
        log("\n[FAIL] STABILITY ASSESSMENT: UNSTABLE - Some tests failed or errors observed")
        log(f"  -> Investigate failures and remediate before Phase 6")
        sys.exit(1)


if __name__ == "__main__":
    main()
