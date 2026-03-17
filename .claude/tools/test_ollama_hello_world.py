#!/usr/bin/env python3
"""
Ollama Hello World Test — With Full Logging
============================================
Tests the canonical local Ollama runtime with a simple inference call.
Shows all logs, errors, and response details.

Usage:
    python3 .claude/tools/test_ollama_hello_world.py

Exit codes:
    0  Success
    1  Connection failed
    2  Model not found
    3  Inference failed
"""

import sys
import json
import urllib.request
import urllib.error
import time
import socket
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path.cwd()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from claudeclockwork.localai.local_ollama_runtime import LocalOllamaRuntimeConfig
except ImportError as e:
    print(f"[ERROR] Cannot import LocalOllamaRuntimeConfig: {e}", file=sys.stderr)
    sys.exit(1)

# Detect environment and get appropriate Ollama URL
def get_ollama_url_for_environment():
    """Get Windows native Ollama URL for current environment (Windows or WSL)."""
    try:
        # Try localhost first (works from Windows)
        sock = socket.create_connection(("127.0.0.1", 11434), timeout=2)
        sock.close()
        return "http://127.0.0.1:11434"
    except:
        try:
            # If localhost fails, try Windows gateway (from WSL)
            sock = socket.create_connection(("172.22.128.1", 11434), timeout=2)
            sock.close()
            return "http://172.22.128.1:11434"
        except:
            return "http://127.0.0.1:11434"  # fallback to SSOT canonical

# Load canonical config
try:
    config = LocalOllamaRuntimeConfig.load()
    BASE_URL = get_ollama_url_for_environment()
    DEFAULT_MODEL = LocalOllamaRuntimeConfig.get_default_model()
    FALLBACK_MODEL = LocalOllamaRuntimeConfig.get_fallback_model()
    CONNECT_TIMEOUT = LocalOllamaRuntimeConfig.get_timeout("connect")
    REQUEST_TIMEOUT = LocalOllamaRuntimeConfig.get_timeout("request")
    print(f"[LOG] Loaded canonical config from .claude/config/local_ollama_runtime.yaml", file=sys.stderr)
except Exception as e:
    print(f"[ERROR] Failed to load canonical config: {e}", file=sys.stderr)
    sys.exit(1)

print(f"[LOG] === OLLAMA HELLO WORLD TEST ===", file=sys.stderr)
print(f"[LOG] Base URL: {BASE_URL}", file=sys.stderr)
print(f"[LOG] Default model: {DEFAULT_MODEL}", file=sys.stderr)
print(f"[LOG] Fallback model: {FALLBACK_MODEL}", file=sys.stderr)
print(f"[LOG] Connect timeout: {CONNECT_TIMEOUT}s", file=sys.stderr)
print(f"[LOG] Request timeout: {REQUEST_TIMEOUT}s", file=sys.stderr)
print()

# Step 1: Check connection
print(f"[STEP 1] Testing connection to {BASE_URL}...", file=sys.stderr)
try:
    url = f"{BASE_URL}/api/tags"
    print(f"[LOG] Requesting: {url}", file=sys.stderr)

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=CONNECT_TIMEOUT) as response:
        data = json.loads(response.read())
        models = data.get("models", [])
        print(f"[SUCCESS] Connected to Ollama. {len(models)} models available.", file=sys.stderr)
        print(f"[LOG] Status code: 200 OK", file=sys.stderr)
except urllib.error.URLError as e:
    print(f"[ERROR] Connection failed: {e}", file=sys.stderr)
    print(f"[ERROR] Ollama not reachable at {BASE_URL}", file=sys.stderr)
    print(f"[ERROR] Make sure Ollama is running: ollama serve", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
    sys.exit(1)

print()

# Step 2: Check if default model is installed
print(f"[STEP 2] Checking if {DEFAULT_MODEL} is installed...", file=sys.stderr)
installed_model = None
for model in models:
    model_name = model.get("name", "")
    if DEFAULT_MODEL in model_name:
        installed_model = model_name
        print(f"[SUCCESS] Found: {model_name}", file=sys.stderr)
        break

if not installed_model:
    print(f"[WARNING] {DEFAULT_MODEL} not found. Trying fallback {FALLBACK_MODEL}...", file=sys.stderr)
    for model in models:
        model_name = model.get("name", "")
        if FALLBACK_MODEL in model_name:
            installed_model = model_name
            print(f"[SUCCESS] Found: {model_name}", file=sys.stderr)
            break

if not installed_model:
    print(f"[ERROR] Neither {DEFAULT_MODEL} nor {FALLBACK_MODEL} found.", file=sys.stderr)
    print(f"[ERROR] Available models: {[m.get('name') for m in models[:5]]}...", file=sys.stderr)
    sys.exit(2)

print()

# Step 3: Run hello-world inference
print(f"[STEP 3] Running hello-world inference with {installed_model}...", file=sys.stderr)
print(f"[LOG] Model: {installed_model}", file=sys.stderr)
print(f"[LOG] Timeout: {REQUEST_TIMEOUT}s", file=sys.stderr)

prompt = "Say 'Hello, World!' and nothing else."
print(f"[LOG] Prompt: {prompt}", file=sys.stderr)
print()

# Build request
payload = json.dumps({
    "model": installed_model,
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "stream": False,
    "options": {
        "temperature": 0.1,
        "num_predict": 100,
    }
}).encode("utf-8")

url = f"{BASE_URL}/api/chat"
print(f"[LOG] Requesting: POST {url}", file=sys.stderr)
print(f"[LOG] Payload size: {len(payload)} bytes", file=sys.stderr)

req = urllib.request.Request(
    url,
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)

# Send request
start_time = time.time()
print(f"[LOG] Sending request...", file=sys.stderr)
print()

try:
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
        elapsed = time.time() - start_time
        status_code = response.status

        response_data = json.loads(response.read())

        print(f"[LOG] Response received in {elapsed:.2f}s", file=sys.stderr)
        print(f"[LOG] Status code: {status_code}", file=sys.stderr)
        print()

        # Extract message
        if "message" in response_data:
            content = response_data["message"].get("content", "")
            print(f"[SUCCESS] === OUTPUT ===", file=sys.stderr)
            print(f"{content}")
            print(f"[LOG] === END OUTPUT ===", file=sys.stderr)
        else:
            print(f"[ERROR] No message in response", file=sys.stderr)
            print(f"[LOG] Full response: {json.dumps(response_data, indent=2)}", file=sys.stderr)
            sys.exit(3)

        # Show metrics
        print()
        print(f"[METRICS]", file=sys.stderr)
        print(f"  Elapsed time: {elapsed:.2f}s", file=sys.stderr)
        print(f"  Prompt tokens: {response_data.get('prompt_eval_count', 0)}", file=sys.stderr)
        print(f"  Completion tokens: {response_data.get('eval_count', 0)}", file=sys.stderr)
        total_tokens = response_data.get('prompt_eval_count', 0) + response_data.get('eval_count', 0)
        tps = total_tokens / elapsed if elapsed > 0 else 0
        print(f"  Tokens/sec: {tps:.2f}", file=sys.stderr)

        print()
        print(f"[SUCCESS] Hello-world test passed! ✅", file=sys.stderr)
        sys.exit(0)

except urllib.error.URLError as e:
    elapsed = time.time() - start_time
    print(f"[ERROR] Request failed after {elapsed:.2f}s: {e}", file=sys.stderr)
    print(f"[ERROR] URL: {url}", file=sys.stderr)
    sys.exit(3)
except json.JSONDecodeError as e:
    elapsed = time.time() - start_time
    print(f"[ERROR] Invalid JSON response after {elapsed:.2f}s: {e}", file=sys.stderr)
    sys.exit(3)
except Exception as e:
    elapsed = time.time() - start_time
    print(f"[ERROR] Unexpected error after {elapsed:.2f}s: {e}", file=sys.stderr)
    sys.exit(3)
