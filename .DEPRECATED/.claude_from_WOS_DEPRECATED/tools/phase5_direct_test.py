#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 5 - Ollama Stability Validation Test (Direct, Simplified)
================================================================

Execute 5-test validation sequence across 2 passes:
1. /api/tags
2. short generate using small/medium model (qwen3:8b)
3. short generate using main heavy model (qwen2.5-72b:docs)
4. one ClaudeClockwork-like run with heavy task
5. repeat once to verify stability

Record: success/failure, latency, HTTP code
"""

import sys
import json
import urllib.request
import urllib.error
import time
from datetime import datetime
import io
import os

# Fix encoding on Windows
if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OLLAMA_BASE_URL = "http://localhost:11434"
TIMEOUT = 180  # Model loads can take 30-60s

class Result:
    def __init__(self, test_num, test_name):
        self.test_num = test_num
        self.test_name = test_name
        self.http_code = None
        self.latency_ms = None
        self.success = False
        self.error = None

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def call_api(method, endpoint, data=None):
    """Call Ollama API and return (status_code, response_text, latency_ms)."""
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
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        raise

def test_1_api_tags():
    """Test 1: /api/tags"""
    result = Result(1, "/api/tags")
    try:
        log("Test 1: /api/tags")
        code, resp, latency = call_api("GET", "/api/tags")
        result.http_code = code
        result.latency_ms = latency

        if code == 200:
            data = json.loads(resp)
            models = len(data.get("models", []))
            log(f"  [OK] HTTP {code}, {models} models, {latency:.0f}ms")
            result.success = True
        else:
            log(f"  [FAIL] HTTP {code}")
            result.error = f"HTTP {code}"
    except Exception as e:
        result.error = str(e)
        log(f"  [FAIL] {e}")

    return result

def test_2_small_model():
    """Test 2: Generate with small model (qwen3:8b)"""
    result = Result(2, "qwen3:8b generate")
    try:
        log("Test 2: Generate with qwen3:8b")

        payload = {
            "model": "qwen3:8b",
            "messages": [{"role": "user", "content": "Write one word."}],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 20}
        }

        code, resp, latency = call_api("POST", "/api/chat", payload)
        result.http_code = code
        result.latency_ms = latency

        if code == 200:
            data = json.loads(resp)
            content = data.get("message", {}).get("content", "")
            eval_count = data.get("eval_count", 0)
            tps = eval_count / (latency / 1000) if latency > 0 else 0
            log(f"  [OK] HTTP {code}, {len(content)} chars, {tps:.1f} tok/s, {latency:.0f}ms")
            result.success = True
        else:
            log(f"  [FAIL] HTTP {code}")
            result.error = f"HTTP {code}"
    except Exception as e:
        result.error = str(e)
        log(f"  [FAIL] {e}")

    return result

def test_3_heavy_model():
    """Test 3: Generate with heavy model (qwen2.5-72b:docs)"""
    result = Result(3, "qwen2.5-72b:docs generate")
    try:
        log("Test 3: Generate with qwen2.5-72b:docs")

        payload = {
            "model": "qwen2.5-72b:docs",
            "messages": [{"role": "user", "content": "Unix epoch in one sentence."}],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 50}
        }

        code, resp, latency = call_api("POST", "/api/chat", payload)
        result.http_code = code
        result.latency_ms = latency

        if code == 200:
            data = json.loads(resp)
            content = data.get("message", {}).get("content", "")
            eval_count = data.get("eval_count", 0)
            tps = eval_count / (latency / 1000) if latency > 0 else 0
            log(f"  [OK] HTTP {code}, {len(content)} chars, {tps:.1f} tok/s, {latency:.0f}ms")
            result.success = True
        else:
            log(f"  [FAIL] HTTP {code}")
            result.error = f"HTTP {code}"
    except Exception as e:
        result.error = str(e)
        log(f"  [FAIL] {e}")

    return result

def test_4_clockwork_sim():
    """Test 4: ClaudeClockwork-like heavy task"""
    result = Result(4, "clockwork-sim heavy task")
    try:
        log("Test 4: ClaudeClockwork-like heavy task")

        payload = {
            "model": "qwen2.5-72b:docs",
            "messages": [{
                "role": "user",
                "content": "Explain git commit in 2 sentences."
            }],
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 100}
        }

        code, resp, latency = call_api("POST", "/api/chat", payload)
        result.http_code = code
        result.latency_ms = latency

        if code == 200:
            data = json.loads(resp)
            content = data.get("message", {}).get("content", "")
            eval_count = data.get("eval_count", 0)
            tps = eval_count / (latency / 1000) if latency > 0 else 0
            log(f"  [OK] HTTP {code}, {len(content)} chars, {tps:.1f} tok/s, {latency:.0f}ms")
            result.success = True
        else:
            log(f"  [FAIL] HTTP {code}")
            result.error = f"HTTP {code}"
    except Exception as e:
        result.error = str(e)
        log(f"  [FAIL] {e}")

    return result

def main():
    log("=" * 70)
    log("PHASE 5 - OLLAMA STABILITY VALIDATION")
    log("=" * 70)

    # Verify connectivity
    try:
        code, _, _ = call_api("GET", "/api/tags")
        if code != 200:
            log("[FAIL] Ollama /api/tags returned HTTP {code}")
            sys.exit(1)
    except Exception as e:
        log(f"[FAIL] Cannot reach Ollama: {e}")
        sys.exit(1)

    log("[OK] Ollama is reachable")
    log("")

    all_results = []

    # Pass 1
    log("PASS 1/2 - Tests 1-4")
    log("-" * 70)
    all_results.append(test_1_api_tags())
    all_results.append(test_2_small_model())
    all_results.append(test_3_heavy_model())
    all_results.append(test_4_clockwork_sim())

    log("")
    log("Waiting 5 seconds between passes...")
    time.sleep(5)

    # Pass 2
    log("")
    log("PASS 2/2 - Tests 1-4 (REPEAT)")
    log("-" * 70)
    all_results.append(test_1_api_tags())
    all_results.append(test_2_small_model())
    all_results.append(test_3_heavy_model())
    all_results.append(test_4_clockwork_sim())

    # Summary
    log("")
    log("=" * 70)
    log("SUMMARY")
    log("=" * 70)

    pass_1 = all_results[0:4]
    pass_2 = all_results[4:8]

    for i, r in enumerate(all_results):
        status = "PASS" if r.success else "FAIL"
        code_str = str(r.http_code) if r.http_code else "ERR"
        latency_str = f"{r.latency_ms:.0f}ms" if r.latency_ms else "N/A"
        error_str = f" ({r.error})" if r.error else ""

        pass_num = (i // 4) + 1
        test_num = (i % 4) + 1
        log(f"  Pass {pass_num}, Test {test_num}: {status} | HTTP {code_str} | {latency_str}{error_str}")

    pass_1_count = sum(1 for r in pass_1 if r.success)
    pass_2_count = sum(1 for r in pass_2 if r.success)
    total_count = len(all_results)
    pass_count = pass_1_count + pass_2_count

    log("")
    log(f"Pass 1: {pass_1_count}/4 tests passed")
    log(f"Pass 2: {pass_2_count}/4 tests passed")
    log(f"Total:  {pass_count}/{total_count} tests passed")

    # Check for error codes
    error_codes = set(r.http_code for r in all_results if r.http_code not in (200, None))

    log("")
    if error_codes:
        log(f"Error codes observed: {error_codes}")

    # Final assessment
    log("")
    if pass_count == total_count and not error_codes:
        log("[OK] STABILITY ASSESSMENT: STABLE")
        log("  All tests passed, no 499/500 errors")
        log("  Proceed to Phase 6: Final report")
        return 0
    else:
        log("[FAIL] STABILITY ASSESSMENT: UNSTABLE")
        log(f"  {total_count - pass_count} test(s) failed or error codes present")
        log("  Investigate and remediate before Phase 6")
        return 1

if __name__ == "__main__":
    sys.exit(main())
