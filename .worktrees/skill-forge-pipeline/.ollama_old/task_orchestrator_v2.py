#!/usr/bin/env python3
"""
Task.md Orchestrator v2 — Pure Ollama Swarm (using ollama library)
Faster, more reliable than curl.
Routes all work to pure Ollama profiles.
NO Claude agents.
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
TASK_MD = PROJECT_ROOT / "Task.md"

def ollama_call(model: str, prompt: str) -> str:
    """Call Ollama profile using ollama library."""
    try:
        response = ollama.generate(model=model, prompt=prompt, stream=False)
        return response.get("response", "").strip()
    except Exception as e:
        print(f"❌ {model} failed: {e}")
        return ""

def main():
    print("\n" + "="*70)
    print("  TASK.MD ORCHESTRATOR v2 — PURE OLLAMA SWARM")
    print("="*70)

    # Load Task.md
    print("\n▶ Loading Task.md...")
    task_md = TASK_MD.read_text()
    print(f"✓ Loaded {len(task_md)} chars")

    # Extract key requirements from Task.md
    print("\n▶ Extracting requirements (qwen3:8b:reasoning)...")
    extract_prompt = """Read this task specification and list EXACTLY what must be done.

TASK:
===
Be concise. List only:
- Requirement A
- Requirement B
- Requirement C
- Requirement D
- Requirement E
- Requirement F

What are these exactly?
"""

    requirements = ollama_call("qwen3:8b", extract_prompt)
    print(f"✓ Requirements:\n{requirements}")

    # Step 1: Have qwen2.5-72b:planner plan implementation
    print("\n▶ Step 1: PLAN (qwen2.5-72b:planner)")
    plan_prompt = """You are planning an implementation of a Flask web application feature.

TASK: Repair the suggested-discussions feature in World of Shadows (Flask backend + frontend).

QUICK PLAN:
1. Which backend services need changes?
2. Which frontend files need changes?
3. Which tests need writing?
4. Which docs need updating?

Be specific. List file names.
"""

    plan = ollama_call("qwen2.5-72b:planner", plan_prompt)
    print(f"✓ Plan:\n{plan}")

    # Step 2: Have qwen2.5-72b:agent break into tasks
    print("\n▶ Step 2: TASK BREAKDOWN (qwen2.5-72b:agent)")
    breakdown_prompt = f"""Break this plan into 10-15 concrete EXECUTABLE tasks.

PLAN:
{plan}

FORMAT:
TASK_1: <name> | ASSIGN: <profile> | WHO: <role>
TASK_2: <name> | ASSIGN: <profile> | WHO: <role>
etc

Profiles available:
- qwen2.5-coder-32b:coding = Python/Flask backend coding
- deepseek-coder-33b:coding = Backup coder
- qwen2.5-coder-32b:integrator = Merge code
- deepseek-coder-33b:reviewer = Code review
- phi4-14b:validator = Check tasks
- qwen3.5-35b:docs = Write docs
- qwen2.5-coder-32b:coding = Write tests

Assign each task to ONE profile. Go.
"""

    tasks = ollama_call("qwen2.5-72b:agent", breakdown_prompt)
    print(f"✓ Task breakdown:\n{tasks}")

    # Step 3: Validate with phi4
    print("\n▶ Step 3: VALIDATE (phi4-14b:validator)")
    validate_prompt = f"""Check if these tasks are COMPLETE, SAFE, and EXECUTABLE.

TASKS:
{tasks}

OUTPUT:
VALID: yes|no
ISSUES: <list any>
FIX: <suggested fix if issues>
"""

    validation = ollama_call("phi4-14b:validator", validate_prompt)
    print(f"✓ Validation:\n{validation}")

    if "no" in validation.lower():
        print("\n❌ Validation failed. Stopping.")
        return 1

    # Step 4: Generate implementation strategy
    print("\n▶ Step 4: IMPLEMENTATION ROADMAP (qwen2.5-72b:reasoning)")
    impl_prompt = f"""Given these tasks, create an implementation roadmap.

TASKS:
{tasks}

ROADMAP:
- Phase 1 (Backend Data): <steps>
- Phase 2 (Backend API): <steps>
- Phase 3 (Frontend Display): <steps>
- Phase 4 (Frontend Management): <steps>
- Phase 5 (Tests): <steps>
- Phase 6 (Docs): <steps>

What order must they be in? Why?
"""

    roadmap = ollama_call("qwen2.5-72b:reasoning", impl_prompt)
    print(f"✓ Roadmap:\n{roadmap}")

    # Step 5: Ready for dispatch
    print("\n" + "="*70)
    print("  ORCHESTRATION COMPLETE")
    print("="*70)
    print("\nRESULTS:")
    print(f"\n1. PLAN:\n{plan}")
    print(f"\n2. TASKS:\n{tasks}")
    print(f"\n3. VALIDATION:\n{validation}")
    print(f"\n4. ROADMAP:\n{roadmap}")

    print("\n" + "-"*70)
    print("NEXT: Dispatch each TASK to its assigned profile for execution")
    print("-"*70)

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
