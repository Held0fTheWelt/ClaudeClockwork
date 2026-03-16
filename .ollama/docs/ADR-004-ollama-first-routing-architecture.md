# ADR-004: Ollama-First Routing Architecture

**Status:** Accepted
**Date:** 2026-03-15
**Stakeholders:** Backend Team, Cost Control, Performance

## Context

The World of Shadows backend needs cost-effective task execution for AI-driven features. Claude API pricing scales quickly:
- Claude Haiku: $0.08/1M input tokens
- Claude Sonnet: $3/1M input tokens
- Claude Opus: $15/1M input tokens

Ollama (open-source, local-first) costs $0 when running on-premise or compatible infrastructure. The decision is to prioritize local execution with intelligent fallback to Claude API for tasks beyond Ollama's capability.

## Decision

Implement **Ollama-first routing with Claude API fallback** based on task escalation levels (L0-L5):

| Level | Target Worker | Model(s) | Use Case | Cost |
|-------|---------------|----------|----------|------|
| **L0** | None | — | Trivial (1 file, no API change) | $0 |
| **L1** | Ollama | qwen2.5-coder:32b, deepseek-coder:33b, phi4:14b | Code drafting, test generation | $0 |
| **L2** | Ollama | qwen2.5:72b, llama3.3:70b | Architecture, module design | $0 |
| **L3** | Claude API | claude-sonnet-4-6 | Performance paths, external API review | ~$0.3 |
| **L4** | Claude API | claude-opus-4-6 | Governance, systemic changes | ~$1.5 |
| **L5** | **User Approval** | — | Orchestrator redesign, breaking changes | Manual |

### Routing Logic

1. **Escalation level 0-2 (L0-L2):** Route to Ollama
   - If Ollama unavailable and `fallback_to_claude=True`: escalate to Claude
   - If `force_ollama=True` and unavailable: return error
2. **Escalation level 3-4 (L3-L4):** Route directly to Claude API
3. **Escalation level 5 (L5):** Stop and ask user for approval

### Fallback Behavior

When Ollama is unavailable for L1/L2 tasks:
- Default (`fallback_to_claude=True`): escalate to Claude Sonnet (L3)
- Strict mode (`force_ollama=True`): fail with clear error message

This ensures feature continuity while maintaining cost targets for the typical case.

## Rationale

### Cost Savings
- **90%+ reduction** for L1-L2 workloads (typical dev tasks)
- Example: 100 tasks/month × 2K tokens = 200K tokens
  - Ollama: $0
  - Claude Haiku: $16/month
  - Savings: $16/month per developer

### Resilience
- Local-first avoids API rate limits and external dependencies
- Fallback to Claude prevents complete service outage
- Graceful degradation: slow ≠ broken

### Scalability
- Ollama models (70B max) fit on consumer-grade GPUs
- No vendor lock-in; can migrate models between providers
- Token budgeting prevents runaway costs

## Alternatives Considered

### 1. Claude-Only
- **Pros:** Simpler implementation, no Ollama dependency
- **Cons:** 10-100x higher costs, vendor lock-in
- **Decision:** Rejected due to cost targets

### 2. Random Routing
- **Pros:** Distributes load
- **Cons:** Unpredictable costs, no capability matching
- **Decision:** Rejected; deterministic routing is better

### 3. Capability-Based Routing
- **Pros:** Route to most capable model for each task
- **Cons:** Overkill for simple tasks, increases latency, complexity
- **Decision:** Rejected; escalation levels are simpler and sufficient

## Consequences

### Positive
- ✅ Cost control: 90%+ savings for typical workloads
- ✅ Reduced Claude API dependency and vendor lock-in
- ✅ Offline capability: works without internet for L1-L2
- ✅ Deterministic routing: predictable, auditable cost

### Negative
- ⚠️ Latency: 70B Ollama models slower than Claude API
  - Ollama 70B on CPU: ~30-60s for 2K tokens
  - Claude Sonnet: ~2-5s for 2K tokens
  - **Tradeoff:** Cost vs speed; acceptable for async tasks
- ⚠️ Infrastructure: Requires local Ollama server (on-premise or dedicated box)
- ⚠️ Model management: Requires operator to load/unload models
- ⚠️ Token budget enforcement: Hard limit prevents runaway costs but may reject legitimate tasks

### How to Mitigate
- Use async task execution to hide Ollama latency
- Pre-load high-use models to reduce startup time
- Implement model caching and prompt caching
- Monitor escalation patterns; escalate frequently = underprovisioned Ollama

## Implementation

See `integration_guide.md` for setup and API usage.

## References

- `.ollama/app/services/task_executor_service.py` — Service adapter
- `.ollama/app/routes/task_routes.py` — REST endpoint
- `.ollama/tests/test_task_executor.py` — Fallback tests
- `.claudeclockwork/` — TaskExecutor, OllamaRouter, CostTracker implementations
