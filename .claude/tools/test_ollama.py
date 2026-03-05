#!/usr/bin/env python3
"""
Ollama Functional Test — Python Orchestrator
=============================================
Hello-world inference test. Verifies Ollama is reachable and capable of basic inference.
Run at session start or after restarting Ollama.

Usage:
    python3 .claude/tools/test_ollama.py

Exit codes:
    0  All tests passed — Ollama operational
    1  Ollama not reachable at localhost:11434
    2  No models installed
    3  Inference failed or returned empty output
"""

import sys
import json
import urllib.request
import time

HELLO_WORLD_PROMPT = (
    "Write a minimal Python function that returns the current timestamp as ISO string. "
    "Just the function body, no imports needed."
)

# Preference order: fastest GPU model first, largest last
CANDIDATE_MODELS = [
    "qwen2.5-coder:14b",
    "qwen2.5-coder:7b",
    "phi4:14b",
    "qwen2.5-coder:32b",
]


def get_installed_models() -> list | None:
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            data = json.loads(r.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return None


def run_inference(model: str) -> tuple:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": HELLO_WORLD_PROMPT}],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 200},
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
            elapsed = time.time() - start
            content = result["message"]["content"]
            eval_count = result.get("eval_count", 0)
            tps = eval_count / elapsed if elapsed > 0 else 0.0
            return content, tps
    except Exception:
        return None, 0.0


def main():
    print("[test-ollama] Checking Ollama reachability...")

    # Step 1: Reachability
    models = get_installed_models()
    if models is None:
        print("[test-ollama] FAIL — Ollama not reachable at localhost:11434")
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
