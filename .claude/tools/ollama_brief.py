#!/usr/bin/env python3
"""
Ollama Workload Tool — Python Orchestrator Agent System
=======================================================
Delegates analysis or implementation work to a local Ollama model.
Claude agents use the output as context or as a correctable draft.

Usage:
    echo "task description" | python3 ollama_brief.py [model] [task_type]
    python3 ollama_brief.py [model] [task_type] < task_prompt.txt

Arguments:
    model       Ollama model name (default: qwen2.5-coder:32b)
    task_type   brief | draft | architecture | review | quick
                  brief        — technical analysis + steps (no code)
                  draft        — complete Python implementation draft
                  architecture — module/placement decision
                  review       — code quality check
                  quick        — 3-5 sentence assessment

Hardware routing (configured at call site):
    GPU (RTX 3080, 10 GB VRAM): qwen2.5-coder:14b, phi4:14b, qwen2.5-coder:7b
    CPU (7950X3D, 64 GB RAM):   qwen2.5-coder:32b, qwen2.5:32b, deepseek-r1:14b

Exit codes:
    0  Success
    1  Ollama unavailable — caller MUST freeze, not skip (see governance/ollama_integration.md)
    2  Usage error
"""

import sys
import json
import urllib.request
import urllib.error

# ── Token limits per task type ─────────────────────────────────────────────────

TOKEN_LIMITS = {
    "brief":        1024,
    "draft":        4096,
    "architecture": 1536,
    "review":       2048,
    "quick":         256,
}

# ── System prompts ─────────────────────────────────────────────────────────────

_BASE_CONTEXT = """Project: Python Orchestrator — console application for autonomous Ollama/Claude agent orchestration.

Module hierarchy (dependency flows DOWN — each layer depends only on layers below):
  main.py → orchestrator.py → agents/* → ollama_client.py / claude_client.py → config.py

Mandatory codebase patterns:
- OllamaUnavailableError must never be silently caught — always re-raise (Freeze Protocol)
- Availability guard before L1+ tasks: check is_available() before any Ollama call
- All paths via config.XYZ — never hardcoded strings
- Structured output: {"status": "ok", "content": ..., "doc_path": ..., "level": ...}
- Spawn prompts must be self-contained: include project context, role, write permissions, governance, task, ollama briefing
- PEP 8: snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE_CASE for constants
- Type hints on all public functions: def foo(x: str) -> dict:
- Max 300 lines per file — split using suffix schema (_routing, _handlers, _utils)
- No circular imports. No upward layer references (agents do not import from orchestrator or main).
- Agents do not communicate directly — coordination goes through orchestrator."""

SYSTEM_PROMPTS = {

    "brief": f"""You are a senior Python developer analyzing a task before implementation.

{_BASE_CONTEXT}

Provide a concise technical briefing:

## Technical Analysis
[Which modules/functions/classes are affected? Core challenge?]

## Implementation Steps
[Numbered, concrete. Reference actual Python stdlib or project module names.]

## Risks & Edge Cases
[Import errors, OllamaUnavailableError propagation, subprocess failures, path issues]

## Open Questions
[Missing context that must be resolved before implementing]

Be specific and actionable. No boilerplate.""",

    "draft": f"""You are a senior Python developer. Write a complete, runnable implementation.

{_BASE_CONTEXT}

Output ONLY runnable Python code. Structure:
1. Complete module file — correct imports, type hints on all public functions, docstrings only where logic is non-obvious
2. Split into multiple files if >300 lines using suffix schema (_routing, _handlers, _utils)
3. requirements.txt additions only if non-stdlib dependency is truly necessary

Apply ALL mandatory patterns listed above without exception.
No explanations outside code comments. Code must be ready for review, not pseudo-code.""",

    "architecture": f"""You are a senior Python architect.

{_BASE_CONTEXT}

Additional placement rules:
- Entry point, REPL, arg parsing → src/main.py
- Task classification, routing → src/orchestrator.py
- Trigger detection, doc naming → src/workflow.py
- All Ollama HTTP calls → src/ollama_client.py
- All claude CLI subprocess calls → src/claude_client.py
- Paths, constants, model lists → src/config.py
- Base agent class → src/agents/base.py
- Agent implementations → src/agents/*.py

Analyze the design decision and provide:

## Architecture Assessment
[Correct module placement? Fits existing hierarchy?]

## Dependency Analysis
[Which modules are affected? Upward dependency risk?]

## Alternative Approaches
[At least one alternative with trade-offs]

## Recommendation
[Clear decision with rationale. Reference the module hierarchy.]

Think long-term. Prioritize loose coupling and correct layer placement.""",

    "review": f"""You are a senior Python code reviewer.

{_BASE_CONTEXT}

Check strictly for:
- OllamaUnavailableError silently swallowed (never acceptable)
- Missing availability guard before L1+ Ollama calls
- Hardcoded paths (must use config.XYZ)
- Missing type hints on public functions
- Circular imports or upward layer references
- Files >300 lines without split
- Agent importing directly from another agent (must go via orchestrator)
- Spawn prompts missing required fields (role, write permissions, governance, task)

## Issues Found
[Each issue: Severity (Critical/Warning/Minor) | File:Line | Description | Fix]

## Overall Assessment
[Pass / Pass with warnings / Fail]

## Required Changes
[Blocking issues that must be fixed. Empty if none.]""",

    "quick": f"""You are a senior Python developer.
{_BASE_CONTEXT}
Give a 3–5 sentence technical assessment. Focus on the single most important point.""",
}

# ── Ollama API ─────────────────────────────────────────────────────────────────

def call_ollama(model: str, task_type: str, user_message: str, timeout: int = 300) -> str:
    system     = SYSTEM_PROMPTS.get(task_type, SYSTEM_PROMPTS["brief"])
    num_tokens = TOKEN_LIMITS.get(task_type, 1024)

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_message},
        ],
        "stream": False,
        "options": {
            "temperature": 0.15,       # low for technical accuracy
            "num_predict": num_tokens,
            "num_ctx":     8192,       # context window
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read())
            return result["message"]["content"]
    except urllib.error.URLError as e:
        print(f"[ollama] Ollama not reachable at localhost:11434 — {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"[ollama] Unexpected response format — {e}", file=sys.stderr)
        sys.exit(1)


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    model     = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5-coder:32b"
    task_type = sys.argv[2] if len(sys.argv) > 2 else "brief"

    task = sys.stdin.read().strip()
    if not task:
        print("[ollama] No task provided via stdin", file=sys.stderr)
        sys.exit(2)

    print(f"[ollama] model={model} | type={task_type} | max_tokens={TOKEN_LIMITS.get(task_type, 1024)}", file=sys.stderr)

    result = call_ollama(model, task_type, task)
    print(result)


if __name__ == "__main__":
    main()
