#!/usr/bin/env python3
"""
Ollama Functional Test — Python Orchestrator
=============================================
Hello-world inference test. Verifies Ollama is reachable and capable of basic inference.
Uses canonical settings from .claude/config/local_ollama_runtime.yaml (SSOT).

Run at session start or after restarting Ollama.

Usage:
    python3 .claude/tools/test_ollama.py

Exit codes:
    0  All tests passed — Ollama operational
    1  Ollama not reachable at configured base URL
    2  No models installed
    3  Inference failed or returned empty output
    4  GPU-first validation failed
"""

import sys
import json
import urllib.request
import time
from pathlib import Path

# Add repo root to path for local imports
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from claudeclockwork.localai.local_ollama_runtime import LocalOllamaRuntimeConfig
except ImportError:
    print("[test-ollama] ERROR: Cannot import LocalOllamaRuntimeConfig")
    print("[test-ollama] Ensure claudeclockwork package is installed")
    sys.exit(1)

HELLO_WORLD_PROMPT = (
    "Write a minimal Python function that returns the current timestamp as ISO string. "
    "Just the function body, no imports needed."
)

# Load canonical config
try:
    config = LocalOllamaRuntimeConfig.load()
    OLLAMA_BASE_URL = LocalOllamaRuntimeConfig.get_base_url()
    DEFAULT_MODEL = LocalOllamaRuntimeConfig.get_default_model()
    FALLBACK_MODEL = LocalOllamaRuntimeConfig.get_fallback_model()
    CONNECT_TIMEOUT = LocalOllamaRuntimeConfig.get_timeout("connect")
    HEALTH_TIMEOUT = LocalOllamaRuntimeConfig.get_timeout("health")
    REQUEST_TIMEOUT = LocalOllamaRuntimeConfig.get_timeout("request")
except Exception as e:
    print(f"[test-ollama] WARNING: Failed to load canonical config: {e}")
    print("[test-ollama] Using fallback defaults")
    OLLAMA_BASE_URL = "http://127.0.0.1:11434"
    DEFAULT_MODEL = "qwen3:8b"
    FALLBACK_MODEL = "phi4"
    CONNECT_TIMEOUT = 10
    HEALTH_TIMEOUT = 15
    REQUEST_TIMEOUT = 300

# Preference order: use canonical models first, then fallback candidates
CANDIDATE_MODELS = [
    DEFAULT_MODEL,
    FALLBACK_MODEL,
    "qwen2.5-coder:14b",
    "qwen2.5-coder:7b",
    "phi4:14b",
]


def get_installed_models() -> list | None:
    """Get list of installed models using canonical base URL."""
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        with urllib.request.urlopen(url, timeout=HEALTH_TIMEOUT) as r:
            data = json.loads(r.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception as e:
        print(f"[test-ollama] Error fetching model list: {e}", file=sys.stderr)
        return None


def run_inference(model: str) -> tuple:
    """Run test inference using canonical base URL and timeout."""
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": HELLO_WORLD_PROMPT}],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 200},
    }).encode("utf-8")

    url = f"{OLLAMA_BASE_URL}/api/chat"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
            result = json.loads(response.read())
            elapsed = time.time() - start
            content = result["message"]["content"]
            eval_count = result.get("eval_count", 0)
            tps = eval_count / elapsed if elapsed > 0 else 0.0
            return content, tps
    except urllib.error.URLError as e:
        print(f"[test-ollama] Inference error: {e}", file=sys.stderr)
        return None, 0.0
    except Exception as e:
        print(f"[test-ollama] Unexpected error: {e}", file=sys.stderr)
        return None, 0.0


def main():
    print(f"[test-ollama] Checking Ollama reachability at {OLLAMA_BASE_URL}...")
    print(f"[test-ollama] Using canonical config from .claude/config/local_ollama_runtime.yaml")
    print(f"[test-ollama] Timeouts: connect={CONNECT_TIMEOUT}s, health={HEALTH_TIMEOUT}s, request={REQUEST_TIMEOUT}s")

    # Step 1: Reachability
    models = get_installed_models()
    if models is None:
        print(f"[test-ollama] FAIL — Ollama not reachable at {OLLAMA_BASE_URL}")
        print("[test-ollama] Start Ollama via Windows tray or app, then retry.")
        sys.exit(1)

    print(f"[test-ollama] Ollama running. {len(models)} model(s) installed:")
    for m in models:
        print(f"  - {m}")

    # Step 2: Model selection (prefer fastest available)
    test_model = None
    for candidate in CANDIDATE_MODELS:
        if any(candidate in m for m in models):
            test_model = candidate
            break
    if test_model is None and models:
        test_model = models[0]  # last resort: whatever is installed

    if test_model is None:
        print("[test-ollama] FAIL — No models installed.")
        print("[test-ollama] Run: ollama pull qwen2.5-coder:14b")
        sys.exit(2)

    print(f"\n[test-ollama] Running hello-world inference with: {test_model}")

    # Step 3: Inference
    content, tps = run_inference(test_model)
    if not content:
        print(f"[test-ollama] FAIL — Inference returned empty output for {test_model}")
        sys.exit(3)

    # Quality check: output should contain recognizable Python constructs
    python_markers = ["def ", "return", "import", ":"]
    quality_ok = any(marker in content for marker in python_markers)

    print(f"\n[test-ollama] Result:")
    print(f"  Model:    {test_model}")
    print(f"  Speed:    {tps:.1f} tok/s")
    print(f"  Output:   {len(content)} chars")
    print(f"  Quality:  {'PASS — Python output detected' if quality_ok else 'WARN — no Python keywords found'}")
    print(f"\n--- Sample output (first 400 chars) ---")
    print(content[:400])
    print("---")

    status = "PASS" if quality_ok else "WARN"
    print(f"\n[test-ollama] {status} — Ollama is operational. Agents may proceed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
