# Ollama Workload Integration

## Core Principle

Ollama handles as much work as possible — Claude Agents verify, correct, and apply project context. Goal: maximum cost reduction on Claude API tokens.

```
Ollama (local model)
  → Raw analysis or complete implementation draft
  → Knows Python APIs, can generate code

Claude Agent (Sonnet)
  → Quality control: does this fit THIS project?
  → Corrects errors (missing type hints, wrong module placement, wrong pattern)
  → Applies project-specific patterns that Ollama doesn't know
  → Final commit-ready code
```

**Effective Task Division:**
- `brief` + `architecture` → Ollama: ~80% of analysis. Claude: verification + decision.
- `draft` → Ollama: ~60–70% of code. Claude: review + corrections + project context.
- `review` → Ollama: complete initial check. Claude: acceptance or escalation.

---

## Hardware Routing

| Device | VRAM/RAM | Models that fit | Optimal usage |
|---|---|---|---|
| **RTX 3080** | 10 GB VRAM | ≤13B Q8 or ≤30B Q4 | GPU inference (~760 GB/s bandwidth) |
| **CPU 7950X3D** | 64 GB DDR5 | up to ~50B Q8 or 70B Q4 | Models that don't fit in VRAM |

**Critical Rule: Hybrid = slow.**
If a model doesn't fit completely in VRAM, Ollama must split layers between RAM and VRAM. PCIe transfer becomes bottleneck → can be slower than pure CPU.

```bash
# Explicitly force CPU (no GPU hybrid):
OLLAMA_NUM_GPU=0 ollama run qwen2.5-coder:32b

# Force GPU (only if model definitely fits):
OLLAMA_NUM_GPU=99 ollama run qwen2.5-coder:14b
```

---

## Model Recommendations

### Primary Models (for daily work)

| Model | Hardware | Task Types | Agent Type | Strength |
|---|---|---|---|---|
| `qwen2.5:72b` / `llama3.3:70b` | CPU (64 GB RAM, Q4) | `brief`, `architecture` | **Infrastructure** (Personaler, Servant, Tester) | Broad reasoning for shortlists + routing |
| `qwen2.5-coder:32b` | CPU (64 GB RAM) | `draft`, `brief` | **Implementation Agent** (≤33b) | Best code quality, completely in RAM |
| `phi4:14b` | GPU (10 GB VRAM) | `architecture`, `brief` | Architecture/Critics (L2+) | Superior reasoning for architecture |
| `qwen2.5-coder:14b` | GPU (10 GB VRAM) | `review`, `quick` | Review tasks | Fast, good for code review |

### Agent → Claude Model Mapping (Canonical)

| Agent Type | Claude Model | Oodle Model |
|---|---|---|
| Infrastructure (Personaler, Servant, Tester, Context Packer) | **Haiku** | **70b/72b** (CPU) |
| Implementation Agent | **max. Sonnet 4.5** | **max. 33b** (qwen2.5-coder:32b, CPU) |
| Architecture Agent (L2) | Sonnet | phi4:14b (GPU) |
| Technical Critic (L3) | Sonnet | phi4:14b (GPU) |
| Systemic Critic (L4) | Sonnet | phi4:14b (GPU) |

### Optional Additions

| Model | Strength | When to use |
|---|---|---|
| `qwen2.5-coder:7b` | Very fast | Trivial checks, L0 tasks |
| `deepseek-r1:14b` | Chain-of-thought reasoning | Complex architecture decisions |
| `qwen2.5:32b` | General reasoning | When coder bias interferes |

---

## Ollama model selection (first-class)

**Canonical policy (static):** `.claude/config/ollama.yaml` — version, state_file path, default_model, global_prompt_budget_chars, global_num_ctx_tokens, runtime options, and profiles (default, execution, coding, review, planning, etc.). One source of truth for policy.

**Canonical runtime state (mutable):** `.claude/state/ollama_model_state.json` — holds `default_model` only. Path may be overridden in config via `state_file`. Changed via the skill or manager, not by editing scripts.

**Skill:** `ollama_model_manage` — actions: list, get, set, validate, profiles. Script-based model switching is not the primary mechanism; use the skill or runtime.

```bash
# List installed models and global default
python3 -m claudeclockwork.cli --skill-id ollama_model_manage --inputs '{"action": "list"}'

# Get global default model
python3 -m claudeclockwork.cli --skill-id ollama_model_manage --inputs '{"action": "get"}'

# Set global default (validates via /api/tags only; alias resolved to installed tag; no auto_pull)
python3 -m claudeclockwork.cli --skill-id ollama_model_manage --inputs '{"action": "set", "model": "qwen2.5-14b:research"}'

# Validate model without switching
python3 -m claudeclockwork.cli --skill-id ollama_model_manage --inputs '{"action": "validate", "model": "phi4:14b"}'

# Show configured profiles and global default
python3 -m claudeclockwork.cli --skill-id ollama_model_manage --inputs '{"action": "profiles"}'
```

**Resolution order (canonical):**
- **Model:** per-invocation override > profile.model > state.default_model > config.default_model
- **Prompt budget (chars):** per-invocation override > profile.prompt_budget_chars > global_prompt_budget_chars
- **num_ctx (tokens):** per-invocation override > profile.num_ctx_tokens > global_num_ctx_tokens

Unknown profiles fall back to global default when `unknown_profile_fallback_to_default: true`. Per-call override does not mutate persistent state. Different agent setups (profiles) keep different configured defaults; the global default does not override profile-specific models.

**Alias-safe validation:** Validation and set use `/api/tags` only; alias is resolved to an installed tag. No `/api/show` or auto_pull; missing models fail clearly.

**Bounded context:** Prompts are limited by profile or global prompt_budget_chars; oversized context is truncated before dispatch. Conservative context defaults are used for CPU-heavy and large models (e.g. planning, reasoning profiles use 7k chars / 4k ctx). Prefer narrow, task-local context over broad repo dumps.

`OllamaAgent(..., model=..., profile=...)` uses the above resolution; `reason()` applies the budget before dispatch. See `claudeclockwork.core.agents.ollama_agent.OllamaAgent`, `claudeclockwork.core.ollama.OllamaModelManager`, and `claudeclockwork.core.ollama.context_budget.apply_budget`.

---

## Tool Invocation

**Importable module:** `<PROJECT_ROOT>/src/ollama_client.py`
**Legacy script:** `.claude/tools/ollama_brief.py`

```python
from src.ollama_client import OllamaClient, OllamaUnavailableError

client = OllamaClient()

# Architecture decision with phi4 on GPU:
result = client.architecture(
    "Should the Ollama client timeout logic live in ollama_client.py or orchestrator.py?"
)

# Implementation draft with 32b on CPU:
result = client.draft(
    "Implement a Python function that checks if a port is open on localhost"
)

# Code review:
code = open("src/orchestrator.py").read()
result = client.review(f"Review this Python code:\n\n{code}")
```

**Bash (for Claude Code integration):**
```bash
# Syntax:
echo "task description" | python3 <PROJECT_ROOT>/.claude/tools/ollama_brief.py [model] [type]

# Types: brief | draft | architecture | review | quick
```

---

## Agent Decision Protocol

### After Receiving Ollama Output — What Does the Claude Agent Check?

**For `brief` / `architecture`:**
```
✓ Does the briefing name correct Python modules? (e.g., ollama_client, not requests)
✓ Is the suggested module placement correct?
✓ Are mandatory patterns mentioned? (OllamaFreeze, Type Hints, max 300 lines)
→ Accept: Use briefing as context
→ Refine: Add context, send again (max 2x)
→ Skip: Ollama unavailable or 2 refinements without improvement
```

**For `draft`:**
```
✓ Are type hints on all public functions present?
✓ PEP 8 followed?
✓ No hardcoded paths? (everything via config.XYZ)
✓ OllamaUnavailableError correctly propagated (not silent)?
✓ File under 300 lines?
→ Accept & Apply: Write code directly to project files
→ Correct & Apply: Correct errors inline, then write
→ Reject: Structure fundamentally wrong (layer violation) → implement manually
```

**For `review`:**
```
✓ Are all critical issues valid (not false positives)?
→ Accept: Use review report as basis for Validation Agent
→ Correct: Remove false positives, add own findings
```

### Refinement Loop (max 2 iterations)

```python
from src.ollama_client import OllamaClient

client = OllamaClient()

# Iteration 1: Basic request
result = client.draft("Implement OllamaClient.call_timed() method")

# Agent checks: too generic? Wrong module placement?
# Iteration 2: With additional context
result = client.draft(
    "Implement OllamaClient.call_timed() method",
    extra_context=(
        "Target file: src/ollama_client.py\n"
        "Must return tuple[str, float] — content and tok/s\n"
        "Must raise OllamaUnavailableError, not return None\n"
        "Use urllib.request only, no requests library"
    )
)
```

---

## When Which Task Type

| Situation | Ollama Type | Model | Expected Claude Delta |
|---|---|---|---|
| Implement new Python function (L1) | `draft` | `qwen2.5-coder:32b` | ~30–40% corrections |
| Architecture decision (L2) | `architecture` | `phi4:14b` | Verification, rarely corrections |
| Code review before Validation Agent | `review` | `qwen2.5-coder:14b` | False positive filter |
| Quick technical question (L0) | `quick` | `qwen2.5-coder:7b` | Direct use |
| Complex system design (L3+) | `architecture` | `deepseek-r1:14b` | Deeper review needed |

---

## When Ollama Is Mandatory vs. Optional vs. Skip

| Escalation Level | Call Ollama? | Type |
|---|---|---|
| L0 — Minor, one file | No — don't call at all (overhead > benefit) | — |
| L1 — Multi-file, clear boundaries | Optional — recommended for >50 lines of code | `brief` or `draft` |
| L2 — Architecture Review | Mandatory | `architecture` |
| L3+ — Critic Review | Mandatory | `architecture` + possibly `review` |

> **Important:** "No" for L0 means: Ollama is not called at all.
> If Ollama is called (L1+) and is not reachable → always FREEZE, never silent continue.

---

## Check Ollama Status

```bash
# Is Ollama running? (recommended — works without PATH)
curl -s http://localhost:11434/api/tags \
  | python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin)['models']]"

# Or: directly via binary
OLLAMA="/c/Users/<username>/AppData/Local/Programs/Ollama/ollama.exe"
"$OLLAMA" list
```

---

## Freeze Protocol — Mandatory on Ollama Failure

**Ollama is not an optional tool — it is the workload foundation.**
A freeze is not a full stop — it is a **partial hold**: only the agent that needs Ollama waits.

### Process on OllamaUnavailableError

```
1. Affected agent (who called Ollama) → stops immediately
   No partial implementation without briefing.

2. Parallel running agents → continue working, preserve results

3. Team Lead outputs FREEZE report:

   ╔══════════════════════════════════════════════════════════╗
   ║  OLLAMA UNAVAILABLE — PARTIAL FREEZE                    ║
   ║                                                          ║
   ║  Frozen:    [Agent + task]                              ║
   ║  Preserved: [List of already completed partial results]  ║
   ║  Waiting:   Ollama restoration at localhost:11434        ║
   ║                                                          ║
   ║  Next steps:                                             ║
   ║  1. Start Ollama (Windows tray or app)                   ║
   ║  2. Test: python3 <PROJECT_ROOT>/src/main.py          ║
   ║           --task "test ollama"                           ║
   ║  3. Resume — preserved results will be passed            ║
   ╚══════════════════════════════════════════════════════════╝

4. No autonomous retry — agent waits for user signal "test ollama" / "resume"
```

### Resume After Restoration

```
User: "test ollama" → PASS
  → Team Lead passes preserved results to frozen agent
  → Catch up Ollama briefing
  → Continue task as if nothing happened
```

**No "skip → continue".** The freeze state remains until Ollama is operational.

---

## test-ollama — Health Check

```bash
python3 <PROJECT_ROOT>/src/main.py --task "test ollama"
```

**What the test checks:**
1. Ollama reachable at `localhost:11434`
2. At least one model installed
3. Inference delivers valid Python output
4. Output of: model name, tok/s, output length, pass/warn

**Exit codes (via test_ollama.py):**
- `0` — PASS: Ollama operational, agents may start
- `1` — FAIL: Ollama not reachable
- `2` — FAIL: No model installed
- `3` — FAIL: Inference failed
# Canonical Ollama Briefing Skill Governance

## Overview
The canonical `ollama_briefing` skill is a standardized mechanism for configuring interactions between Claude and Ollama models. It ensures consistent, secure, and efficient communication across different environments by enforcing best practices and predefined policies.

## Usage
This skill must be used whenever integrating Claude with Ollama models to ensure alignment with governance requirements. Developers and system administrators are responsible for defining model parameters, input/output formats, and error handling in the briefing configuration files.

## Configuration
The `ollama_briefing` skill is configured via a YAML file located at `.claude/config/ollama_briefing.yml`. Required fields include:
- `model_name`: The name of the Ollama model to be used.
- `temperature`: Controls randomness in responses (0.0–1.0).
- `max_tokens`: Maximum output length.

Changes to this configuration must follow the organization's change control process for governance compliance.

## Runtime Policy
The skill is activated during initial setup or when updating Ollama integrations. Runtime monitoring includes:
- Success rate of model calls.
- Response time thresholds.
- Error rates and handling.

Compliance audits are conducted periodically to ensure adherence to predefined policies, with non-compliant instances requiring corrective action within 72 hours.