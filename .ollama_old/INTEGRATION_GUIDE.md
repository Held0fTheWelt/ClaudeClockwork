# Ollama Integration Guide

The `.ollama/` folder is a **completely standalone module** for Ollama-based task execution with Claude API fallback. It has **zero dependencies** on the Flask backend and can be used independently.

## Installation

1. **Install claudeclockwork package:**
   ```bash
   pip install -e .clockwork_integration/
   ```

2. **Set environment variables** (see `.env.example` below)

3. **Import and use in any Python code:**
   ```python
   from app.services import TaskExecutorService

   service = TaskExecutorService()
   result = service.execute_task(
       task_id="my_task",
       escalation_level=1,  # L1: code drafting
       inputs={"prompt": "Write a test suite for this function"},
   )

   print(f"Success: {result['success']}")
   print(f"Output: {result['output']}")
   print(f"Cost: {result['cost_formatted']}")
   ```

## Environment Variables

Add to `.env` at repo root:

```bash
# Ollama Routing (from ADR-004)
ANTHROPIC_API_KEY=sk-ant-...       # Required for L3-L4 tasks (Claude API)
OLLAMA_HOST=localhost              # Ollama server hostname
OLLAMA_PORT=11434                  # Ollama server port
OLLAMA_FALLBACK_TO_CLAUDE=true     # Fallback L1/L2 to Claude when Ollama unavailable
```

## Escalation Levels

| Level | Target | Use Case | Cost |
|-------|--------|----------|------|
| **L0** | None | Trivial (1 file, no API change) | $0 |
| **L1** | Ollama | Code drafting, test generation | $0 |
| **L2** | Ollama | Architecture, module design | $0 |
| **L3** | Claude API | Performance paths, external API review | ~$0.3 |
| **L4** | Claude API | Governance, systemic changes | ~$1.5 |
| **L5** | Stop | User approval required | N/A |

See `docs/ADR-004-ollama-first-routing-architecture.md` for full routing logic.

## API

### TaskExecutorService (Singleton)

```python
from app.services import TaskExecutorService

service = TaskExecutorService()
```

#### Methods

**`is_available() -> bool`**
- Returns True if TaskExecutor is initialized and ready.
- Returns False if claudeclockwork is not installed.

**`health_check() -> Dict[str, Any]`**
- Checks Ollama availability and budget status.
- Returns:
  ```python
  {
      "available": True,
      "ollama_available": True,  # Can reach Ollama server
      "budget_status": "ok" | "low" | "exceeded",
      "total_cost": 0.35,
      "total_tokens": 1500,
  }
  ```

**`execute_task(task_id, escalation_level, inputs, preferred_models=None, force_ollama=False) -> Dict[str, Any]`**

Execute a task with intelligent routing.

**Args:**
- `task_id` (str): Task identifier (for logging and routing)
- `escalation_level` (int): 0-5 (L0-L5)
- `inputs` (dict): Must contain `"prompt"` key; optionally `"system_prompt"`
  ```python
  inputs = {
      "prompt": "Write a test suite for mail_service.py",
      "system_prompt": "You are a senior backend engineer...",  # Optional
  }
  ```
- `preferred_models` (list, optional): Preferred model names to try first
- `force_ollama` (bool): If True, fail rather than fall back to Claude

**Returns:**
```python
{
    "success": True,
    "target_worker": "ollama" | "claude_api" | "stop_ask_user",
    "model": "qwen2.5-coder:32b",
    "output": "The generated code/text",
    "cost": 0.0,
    "cost_formatted": "$0.00",
    "tokens_used": 500,
    "latency_ms": 5000.0,
    "error": None,  # Error message if success=False
}
```

**`get_stats() -> Dict[str, Any]`**
- Returns cumulative cost and token usage:
  ```python
  {
      "total_cost": 0.35,
      "total_tokens": 1500,
      "token_limit": 10000,
  }
  ```

## Examples

### Example 1: Simple Code Generation (L1)

```python
from app.services import TaskExecutorService

service = TaskExecutorService()

if not service.is_available():
    print("Ollama service not available")
    exit(1)

result = service.execute_task(
    task_id="generate_docstrings",
    escalation_level=1,  # Code drafting
    inputs={
        "prompt": "Add docstrings to this function",
        "system_prompt": "You are a Python expert. Add Google-style docstrings.",
    },
)

if result["success"]:
    print(f"Generated output (via {result['model']}):")
    print(result["output"])
    print(f"Cost: {result['cost_formatted']}")
else:
    print(f"Error: {result['error']}")
```

### Example 2: Architecture Decision (L2)

```python
from app.services import TaskExecutorService

service = TaskExecutorService()

result = service.execute_task(
    task_id="design_caching_layer",
    escalation_level=2,  # Architecture
    inputs={
        "prompt": "Design a caching layer for our forum API. Consider: cache invalidation, memory limits, TTL strategies.",
    },
    preferred_models=["qwen2.5:72b"],  # Prefer 72B model for reasoning
)

print(f"Architecture proposal via {result['model']}:")
print(result["output"])
print(f"Tokens used: {result['tokens_used']}")
print(f"Latency: {result['latency_ms']}ms")
```

### Example 3: Health Check Before Task

```python
from app.services import TaskExecutorService

service = TaskExecutorService()
health = service.health_check()

if not health["available"]:
    print(f"Service unavailable: {health['error']}")
    exit(1)

if not health["ollama_available"]:
    print("Ollama unavailable; will fall back to Claude API")

if health["budget_status"] == "exceeded":
    print("ERROR: Token budget exceeded!")
    exit(1)

print(f"Ollama available: {health['ollama_available']}")
print(f"Budget status: {health['budget_status']}")
print(f"Cost so far: ${health['total_cost']:.2f}")

# Safe to execute tasks
result = service.execute_task(...)
```

### Example 4: Force Ollama (No Fallback)

```python
from app.services import TaskExecutorService

service = TaskExecutorService()

result = service.execute_task(
    task_id="local_only_task",
    escalation_level=1,
    inputs={"prompt": "..."},
    force_ollama=True,  # Fail if Ollama unavailable
)

if not result["success"]:
    print(f"Local execution failed (Ollama unavailable): {result['error']}")
```

## Testing

Run tests without Flask:

```bash
cd .ollama
python -m pytest tests/test_task_executor_service.py -v
```

Test coverage:
- Input validation (missing prompt, invalid escalation level)
- Ollama unavailability and fallback behavior
- Force Ollama mode
- Cost tracking (Ollama $0, Claude nonzero)
- L5 escalation (stop and ask user)
- Healthy execution flow

## Backend Integration (Optional)

To expose this via Flask routes, the backend can import and call:

```python
# In backend/app/api/v1/some_routes.py
from app.services import TaskExecutorService

@some_blueprint.route("/api/v1/tasks", methods=["POST"])
@jwt_required()
def execute_task():
    service = TaskExecutorService()

    if not service.is_available():
        return jsonify({"error": "Task executor not available"}), 503

    data = request.get_json()
    result = service.execute_task(
        task_id=data["task_id"],
        escalation_level=data["escalation_level"],
        inputs=data["inputs"],
    )

    return jsonify(result)
```

But this is **optional**. The `.ollama/` module works standalone.

## Troubleshooting

**"claudeclockwork not installed"**
```bash
pip install -e .clockwork_integration/
```

**"Ollama unavailable"**
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Or set `OLLAMA_FALLBACK_TO_CLAUDE=true` to allow Claude fallback

**"Token budget exceeded"**
- Check `service.get_stats()` to see cumulative usage
- Implement token budgeting in your application

**"ANTHROPIC_API_KEY not set"**
- Required for L3-L4 tasks
- Set in `.env` or export before running
- If not set and L3-L4 task is routed: Claude call will fail

## Architecture Decision

See `docs/ADR-004-ollama-first-routing-architecture.md` for:
- Cost analysis and routing matrix
- Fallback behavior and consequences
- Alternatives considered
