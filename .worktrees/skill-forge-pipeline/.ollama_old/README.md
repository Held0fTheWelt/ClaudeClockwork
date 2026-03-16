# .ollama — Standalone Task Execution Service

**Completely isolated from the Flask backend.**

This folder contains a pure Python service for intelligent task routing between Ollama (local, $0) and Claude API (cloud, $$$) based on task complexity.

## Quick Start

1. **Install claudeclockwork:**
   ```bash
   pip install -e .clockwork_integration/
   ```

2. **Set env vars** (copy from `.env.example`)

3. **Use in any Python code:**
   ```python
   from app.services import TaskExecutorService

   service = TaskExecutorService()
   result = service.execute_task(
       task_id="my_task",
       escalation_level=1,  # L1: code drafting (Ollama)
       inputs={"prompt": "Write a test suite..."},
   )

   print(f"Success: {result['success']}")
   print(f"Cost: {result['cost_formatted']}")
   ```

## Files

| File | Purpose |
|------|---------|
| `app/services.py` | `TaskExecutorService` singleton adapter (pure Python, no Flask) |
| `tests/test_task_executor_service.py` | Unit tests (mocked, no Ollama required) |
| `docs/ADR-004-ollama-first-routing-architecture.md` | Routing architecture decision |
| `INTEGRATION_GUIDE.md` | Full API documentation and examples |
| `.env.example` | Environment variable template |

## Routing Matrix

| Level | Target | Models | Cost | Use Case |
|-------|--------|--------|------|----------|
| **L0** | None | — | $0 | Trivial (1 file, no API change) |
| **L1** | Ollama | qwen2.5-coder:32b | $0 | Code drafting, testing |
| **L2** | Ollama | qwen2.5:72b | $0 | Architecture, modules |
| **L3** | Claude API | claude-sonnet-4-6 | ~$0.3 | Performance, API review |
| **L4** | Claude API | claude-opus-4-6 | ~$1.5 | Governance, systemic |
| **L5** | Stop | — | N/A | User approval required |

## Key Features

✅ **Standalone** — Zero Flask dependency; use in any Python code
✅ **Graceful degradation** — Ollama unavailable? Fall back to Claude
✅ **Cost control** — 90%+ savings for L1-L2 tasks
✅ **Testable** — Mocked tests, no external dependencies
✅ **Documented** — ADR-004, integration guide, inline examples

## Testing

```bash
cd .ollama
python -m pytest tests/ -v
```

## Troubleshooting

**"claudeclockwork not installed"**
→ `pip install -e .clockwork_integration/`

**"Ollama unavailable"**
→ Set `OLLAMA_FALLBACK_TO_CLAUDE=true` or start Ollama server

**"ANTHROPIC_API_KEY not set"**
→ Required for L3-L4 tasks; set in `.env`

See `INTEGRATION_GUIDE.md` for full troubleshooting.

## Architecture

See `docs/ADR-004-ollama-first-routing-architecture.md` for:
- Cost analysis
- Fallback behavior
- Consequences and tradeoffs
- Alternatives considered
