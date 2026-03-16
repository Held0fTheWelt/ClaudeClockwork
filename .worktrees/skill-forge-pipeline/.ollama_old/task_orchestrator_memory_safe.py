#!/usr/bin/env python3
"""
Task.md Orchestrator — MEMORY SAFE VERSION
Uses ONLY small models (8B/14B) that fit in 10GB VRAM
Prevents OOM crashes from 35B/70B models
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
TASK_MD = PROJECT_ROOT / "Task.md"

def ollama_call(model: str, prompt: str, timeout: int = 120) -> str:
    """Call Ollama profile using ollama library."""
    try:
        print(f"  → {model}...", end=" ", flush=True)
        response = ollama.generate(model=model, prompt=prompt, stream=False)
        result = response.get("response", "").strip()
        print(f"✓ ({len(result)} chars)")
        return result
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"✗ {error_msg}")
        return ""

def main():
    print("\n" + "="*70)
    print("  TASK.MD ORCHESTRATOR — MEMORY SAFE (8B/14B only)")
    print("="*70)

    # Load Task.md
    print("\n▶ Loading Task.md...")
    task_md = TASK_MD.read_text()
    print(f"✓ Loaded {len(task_md)} chars\n")

    # Step 1: Extract with 8B model (fits in VRAM)
    print("▶ Step 1: PLANNING (qwen3-8b:reasoning — 8B, memory-safe)")
    plan_prompt = f"""You are a project architect. Read this Task.md specification and create a high-level implementation plan.

TASK.MD (first 3000 chars):
{task_md[:3000]}
[... full spec in repo ...]

OUTPUT EXACTLY THIS FORMAT:
REQUIREMENTS: [A-F with brief descriptions]
FILES_TO_CHANGE: [list backend, frontend, tests, docs files]
EXECUTION_ORDER: [step 1, step 2, ... step N]
CRITICAL_DEPENDENCIES: [what must be done first]
"""

    plan = ollama_call("qwen3-8b:reasoning", plan_prompt)
    if plan:
        print(f"✓ Plan (first 300 chars): {plan[:300]}\n")
    else:
        print("⚠ Plan generation failed\n")
        return False

    # Step 2: Break into tasks with 14B model
    print("▶ Step 2: TASK BREAKDOWN (phi4:14b:validator — 14B, fits in VRAM)")
    breakdown_prompt = f"""Break this high-level plan into 10-15 SPECIFIC EXECUTABLE TASKS.

PLAN:
{plan[:1500] if plan else 'See above'}

For EACH task, output:
TASK_N: [1 sentence what to do]
COMPONENT: [backend/frontend/tests/docs]
PROFILE: [which Ollama model should do this]
PRIORITY: [must be before X, Y, Z]

Use these profiles:
- qwen2.5-coder-32b:coding for Python/Flask code
- deepseek-coder-33b:coding for backup coding
- deepseek-coder-33b:reviewer for code review
- qwen3.5-35b:docs for documentation (large task)
- phi4-14b:validator for validation tasks
"""

    tasks = ollama_call("phi4-14b:validator", breakdown_prompt)
    if tasks:
        print(f"✓ Tasks created (first 400 chars): {tasks[:400]}\n")
    else:
        print("⚠ Task breakdown failed\n")
        return False

    # Step 3: Validate task list
    print("▶ Step 3: VALIDATION (qwen3-8b:validator — 8B validation)")
    validation_prompt = f"""Validate that these tasks will actually implement Task.md requirements B-F.

TASKS:
{tasks[:1500] if tasks else 'See above'}

Check:
1. ✓ or ✗ All requirements B-F covered?
2. ✓ or ✗ No circular dependencies?
3. ✓ or ✗ Each task is concrete and assignable?
4. ✓ or ✗ Resource requirements reasonable?

OUTPUT:
VALIDATION: [PASS/FAIL]
ISSUES: [list any issues, or "None"]
RECOMMENDATION: [proceed, revise tasks, or stop]
"""

    validation = ollama_call("qwen3-8b:validator", validation_prompt)
    if validation:
        print(f"✓ Validation complete:\n{validation}\n")
    else:
        print("⚠ Validation failed\n")

    # Step 4: Create roadmap
    print("▶ Step 4: EXECUTION ROADMAP (phi4:14b:validator — roadmap generation)")
    roadmap_prompt = f"""Create a detailed execution roadmap for implementing Task.md.

VALIDATED TASKS:
{tasks[:1500] if tasks else 'See above'}

ROADMAP FORMAT:
PHASE 1: [parallel tasks that can run together]
  - Task X (assigned to Y model)
  - Task Y (assigned to Z model)

PHASE 2: [next set of parallel tasks]
  - ...

PHASE N: [final integration/testing/docs]

Also output:
TOTAL_TASKS: [count]
ESTIMATED_STAGES: [how many phases]
GO_NO_GO: [GO if all ready, NO_GO if issues found]
"""

    roadmap = ollama_call("phi4-14b:validator", roadmap_prompt)
    if roadmap:
        print(f"✓ Roadmap generated:\n{roadmap}\n")
    else:
        print("⚠ Roadmap generation failed\n")

    # Summary
    print("\n" + "="*70)
    print("  ✓ ORCHESTRATION COMPLETE")
    print("="*70)
    print("\nNEXT: Dispatch tasks to specialized Ollama agents")
    print("Each task routes to its assigned model for actual implementation\n")

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
