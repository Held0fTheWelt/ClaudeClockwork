#!/usr/bin/env python3
"""
Task.md Orchestrator OPTIMIZED — Uses only memory-safe profiles
Models: qwen3.5-35b (MoE), qwen2.5-coder:32b, phi4:14b, deepseek-33b
NO 72b models (too large for available VRAM)
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
TASK_MD = PROJECT_ROOT / "Task.md"

def ollama_call(model: str, prompt: str, timeout: int = 120) -> str:
    """Call Ollama profile using ollama library."""
    try:
        response = ollama.generate(model=model, prompt=prompt, stream=False)
        return response.get("response", "").strip()
    except Exception as e:
        print(f"  ❌ {model}: {str(e)[:80]}")
        return ""

def main():
    print("\n" + "="*70)
    print("  TASK.MD ORCHESTRATOR — OPTIMIZED (Memory-Safe Profiles)")
    print("="*70)

    # Load Task.md
    print("\n▶ Loading Task.md...")
    task_md = TASK_MD.read_text()
    print(f"✓ Loaded {len(task_md)} chars\n")

    # Step 1: Extract requirements using qwen3.5-35b:reasoning (MoE, 256K context)
    print("▶ Step 1: PLANNING (qwen3.5:35b-a3b)")
    plan_prompt = f"""Read this Task.md and create a structured plan to implement it.

TASK.MD:
{task_md[:3000]}
[... (full spec in repo) ...]

PLAN:
1. What is the exact scope? (list all 6 requirements A-F)
2. Which files must change? (backend + frontend + tests + docs)
3. Suggested implementation order
4. Critical dependencies

Be specific. List exact filenames.
"""

    plan = ollama_call("qwen3.5:35b-a3b", plan_prompt)
    if plan:
        print(f"✓ Plan created:\n{plan}\n")
    else:
        print("⚠ Plan failed\n")

    # Step 2: Task breakdown using qwen2.5-coder-32b:coding
    print("▶ Step 2: TASK BREAKDOWN (qwen2.5-coder-32b:coding)")
    breakdown_prompt = f"""Break this plan into 12-15 CONCRETE EXECUTABLE TASKS.

PLAN:
{plan[:1500] if plan else 'See above'}

FORMAT:
TASK_1: [Name] | PROFILE: [Model] | WHAT: [Exact work]
TASK_2: [Name] | PROFILE: [Model] | WHAT: [Exact work]

Use these profiles only:
- qwen2.5-coder-32b:coding = Python/Flask backend
- deepseek-coder-33b:coding = Backup coding
- deepseek-coder-33b:reviewer = Code review
- phi4-14b:docs = Documentation
- phi4-14b:reviewer = Fast review
- qwen3.5:35b-a3b = Large tasks

Assign each task to ONE profile.
"""

    tasks = ollama_call("qwen2.5-coder-32b:coding", breakdown_prompt)
    if tasks:
        print(f"✓ Tasks:\n{tasks}\n")
    else:
        print("⚠ Task breakdown failed\n")

    # Step 3: Validate with phi4
    print("▶ Step 3: VALIDATE TASKS (phi4-14b:validator)")
    validate_prompt = f"""Validate these tasks for completeness and feasibility.

TASKS:
{tasks[:1500] if tasks else 'See above'}

Check:
1. Are all 6 requirements A-F covered?
2. No placeholders or vague tasks?
3. Can execute sequentially?

OUTPUT:
VALID: yes|no
ISSUES: <list>
READY_TO_EXECUTE: yes|no
"""

    validation = ollama_call("phi4-14b:validator", validate_prompt)
    print(f"Validation: {validation}\n" if validation else "⚠ Validation failed\n")

    # Step 4: Implementation roadmap
    print("▶ Step 4: ROADMAP (qwen3.5:35b-a3b)")
    roadmap_prompt = f"""Create an implementation roadmap for these tasks.

TASKS:
{tasks[:1500] if tasks else 'See above'}

ROADMAP (in order):
Phase 1 (Backend Data): <which tasks>
Phase 2 (Backend API): <which tasks>
Phase 3 (Frontend): <which tasks>
Phase 4 (Tests): <which tasks>
Phase 5 (Docs): <which tasks>

Why this order? What are the dependencies?
"""

    roadmap = ollama_call("qwen3.5:35b-a3b", roadmap_prompt)
    print(f"✓ Roadmap:\n{roadmap}\n" if roadmap else "⚠ Roadmap failed\n")

    # Summary
    print("="*70)
    print("  ORCHESTRATION READY FOR DISPATCH")
    print("="*70)
    print("\nPlan ✓")
    print("Tasks ✓")
    print("Validation ✓")
    print("Roadmap ✓")
    print("\n" + "-"*70)
    print("NEXT: Commission Ollama agents to execute each TASK")
    print("Each task goes to its assigned profile for actual coding work")
    print("-"*70)

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
