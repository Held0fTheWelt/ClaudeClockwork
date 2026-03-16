#!/usr/bin/env python3
"""
Task.md Orchestrator — Pure Ollama Agent Swarm Execution
Routes work to Ollama profiles (qwen2.5-72b:planner, qwen2.5-coder-32b:coding, etc.)
NO Claude agents. Only Ollama.
"""

import subprocess
import json
import sys
from pathlib import Path

OLLAMA_HOST = "http://localhost:11434"
PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
TASK_MD = PROJECT_ROOT / "Task.md"

def call_ollama(model: str, prompt: str, temperature: float = 0.1) -> str:
    """Call Ollama profile and get response."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", f"{OLLAMA_HOST}/api/generate",
             "-d", json.dumps({
                 "model": model,
                 "prompt": prompt,
                 "stream": False,
                 "temperature": temperature,
             })],
            capture_output=True,
            text=True,
            timeout=300
        )
        data = json.loads(result.stdout)
        return data.get("response", "").strip()
    except Exception as e:
        print(f"❌ Ollama call failed ({model}): {e}")
        return ""

def main():
    print("\n" + "="*70)
    print("  TASK.MD ORCHESTRATOR — PURE OLLAMA SWARM")
    print("="*70)

    # Step 1: Read Task.md
    print("\n▶ Step 1: Read Task.md")
    if not TASK_MD.exists():
        print(f"❌ Task.md not found at {TASK_MD}")
        return 1

    task_content = TASK_MD.read_text()
    print(f"✓ Task.md loaded ({len(task_content)} chars)")

    # Step 2: Use qwen2.5-72b:planner to analyze and plan
    print("\n▶ Step 2: Planner — Break down Task.md requirements (qwen2.5-72b:planner)")
    planner_prompt = f"""You are the Swarm Planner. Analyze this task and break it down into executable steps.

TASK:
{task_content}

OUTPUT FORMAT (use these exact headers):
## Exact Scope
- Requirement A: <what it is>
- Requirement B: <what it is>
- (etc for each requirement)

## Implementation Strategy
- Phase 1: <step>
- Phase 2: <step>
- (etc)

## Critical Dependencies
- <if X must happen before Y, state it>

## Which Ollama profiles are needed
- For <task>, use: <profile>
- (etc)

## Estimated Effort
- Backend changes: <files/lines>
- Frontend changes: <files/lines>
- Tests: <test cases>
- Docs: <pages/sections>

Go.
"""

    plan = call_ollama("qwen2.5-72b:planner", planner_prompt, temperature=0.35)
    if not plan:
        print("❌ Planner failed")
        return 1
    print("✓ Plan created:")
    print(plan)

    # Step 3: Task Creator — Decompose into concrete tasks
    print("\n▶ Step 3: Task Creator — Decompose into executable tasks (qwen2.5-72b:agent)")
    creator_prompt = f"""You are the Task Creator. Take this plan and break it into concrete tasks that can be executed by specialized Ollama agents.

PLAN:
{plan}

OUTPUT: List each task as:
TASK_1: <name> | PROFILE: <qwen2.5-coder-32b:coding | deepseek-coder-33b:reviewer | etc> | DESCRIPTION: <what to do>
TASK_2: <name> | PROFILE: <...> | DESCRIPTION: <...>
(etc)

Each task must be:
- Specific and actionable
- Assigned to exactly one profile
- Executable independently or in sequence

Go.
"""

    tasks = call_ollama("qwen2.5-72b:agent", creator_prompt, temperature=0.2)
    if not tasks:
        print("❌ Task Creator failed")
        return 1
    print("✓ Tasks created:")
    print(tasks)

    # Step 4: Validator — Check if tasks are valid before execution
    print("\n▶ Step 4: Validator — Validate tasks (phi4-14b:validator)")
    validator_prompt = f"""You are the Task Validator. Check if these tasks are complete, consistent, and safe to execute.

TASKS:
{tasks}

ORIGINAL TASK:
{task_content}

For each task:
1. Is it complete (has all required info)?
2. Is it consistent with the original requirements?
3. Is it safe (no destructive operations without approval)?
4. Is it feasible (can it be executed)?

OUTPUT:
VALIDATION: <PASS | FAIL>
ISSUES: <list any issues>
RECOMMENDATION: <proceed | clarify | reject>

Go.
"""

    validation = call_ollama("phi4-14b:validator", validator_prompt, temperature=0.15)
    print("✓ Validation result:")
    print(validation)

    if "FAIL" in validation or "reject" in validation.lower():
        print("❌ Validation failed — stopping")
        return 1

    # Step 5: Execute tasks with appropriate profiles
    print("\n▶ Step 5: Execute tasks with Ollama profiles")
    print("⚠ This requires dispatching to individual coding/reviewer/docs profiles")
    print("⚠ These tasks need actual implementation (Python/JS/HTML changes)")
    print("\nTo fully execute Task.md, dispatch each task to:")
    print("  - Coding tasks → qwen2.5-coder-32b:coding")
    print("  - Review tasks → deepseek-coder-33b:reviewer")
    print("  - Docs tasks → qwen3.5-35b:docs")
    print("  - Test tasks → qwen2.5-coder-32b:coding")

    # Step 6: Summarizer — Prepare final report for Claude Code
    print("\n▶ Step 6: Summarizer — Prepare final report (qwen2.5-72b:summarizer)")
    summarizer_prompt = f"""You are the Summarizer. Prepare a final report of what was done.

PLAN:
{plan}

TASKS:
{tasks}

OUTPUT:
## What was executed
<summary>

## Files changed
<list>

## Routes added/changed
<list>

## Tests added
<list>

## Docs updated
<list>

## Wiki solution chosen
<payload-only or dedicated endpoint>

## Remaining work (if any)
<list>

## Commit hashes
<if commits were made>

Go.
"""

    summary = call_ollama("qwen2.5-72b:summarizer", summarizer_prompt, temperature=0.25)
    print("✓ Summary generated:")
    print(summary)

    print("\n" + "="*70)
    print("  ORCHESTRATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Dispatch each task to its assigned Ollama profile")
    print("2. Coder profiles write actual code to files")
    print("3. Create commits after each major change")
    print("4. Reviewer profiles validate code")
    print("5. Docs profiles update documentation")

    return 0

if __name__ == "__main__":
    sys.exit(main())
