#!/usr/bin/env python3
"""Diagnose Ollama integration issues"""
import subprocess
import json
import urllib.request

print("[DIAGNOSIS] Ollama Integration Issues\n")

# Issue 1: Context window mismatch
print("1. Context Window Mismatch:")
print("   - Error: n_ctx_seq (16384) < n_ctx_train (32768)")
print("   - Cause: Models trained with 32K context but running with 16K")
print("   - Fix: Use models with matching context or reduce prompt size")
print("   - Action: Use smaller context models or split prompts\n")

# Issue 2: Timeouts with complex prompts
print("2. Timeout Issues:")
print("   - Cause: Long prompts + small context = slower processing")
print("   - Fix: Use faster models or shorter prompts")
print("   - Models to use:")

# List available models and their recommended uses
models_info = {
    "qwen2.5-14b:agent": "FAST, good for code, low latency",
    "qwen2.5-coder-32b:coding": "MEDIUM, specialized for code",
    "phi4:14b": "FAST, lightweight, good for reviews",
    "qwen3-8b": "VERY FAST, small, reasoning",
    "deepseek-coder-33b:coding": "GOOD for complex code, slower"
}

for model, desc in models_info.items():
    print(f"     - {model:40} {desc}")

print("\n3. Configuration Recommendations:")
print("   - Use qwen2.5-14b:agent for test generation (best balance)")
print("   - Use phi4:14b for code review (fastest)")
print("   - Keep prompts under 1000 tokens")
print("   - Split large tasks into smaller subtasks")
print("   - Use --nostream for non-interactive calls\n")

# Test with recommended model
print("4. Testing qwen2.5-14b:agent...")
try:
    result = subprocess.run(
        ["ollama", "run", "qwen2.5-14b:agent", "Say OK"],
        capture_output=True,
        text=True,
        timeout=30
    )
    if "OK" in result.stdout:
        print("   [OK] Model responds quickly\n")
    else:
        print(f"   [WARN] Response: {result.stdout[:50]}...\n")
except subprocess.TimeoutExpired:
    print("   [FAIL] Timeout - model may be loading\n")
except Exception as e:
    print(f"   [ERROR] {e}\n")

print("[SOLUTION] Use Ollama with proper context and fast models")
