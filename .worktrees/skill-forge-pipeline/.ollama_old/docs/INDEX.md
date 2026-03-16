# Ollama Integration Documentation Index

Complete guide to Ollama routing, integration, troubleshooting, and operations.

## Architecture & Decisions

### [ADR-004: Ollama-First Routing Architecture](ADR-004-ollama-first-routing-architecture.md)
- **Purpose**: Explains the cost-driven routing decision
- **Audience**: Architects, product managers, cost analysts
- **Key topics**:
  - Escalation levels (L0-L5) and model selection
  - Cost analysis: Ollama ($0) vs Claude Haiku/Sonnet/Opus
  - Fallback behavior and consequences
  - Alternatives considered

**Read first if you need to understand WHY we route to Ollama.**

### [ADR-003: Token Budgeting Strategy](ADR-003-token-budgeting-strategy.md)
- **Purpose**: Cost control mechanisms across both Ollama and Claude
- **Audience**: Operators, product, engineers
- **Key topics**:
  - Three-tier budgeting (per-request, session, system-wide)
  - Token limits and cost alerts
  - Pricing model reference

**Read if you need to understand cost tracking and limits.**

---

## Integration & Usage

### [INTEGRATION_GUIDE.md](../INTEGRATION_GUIDE.md) 📌 START HERE
- **Purpose**: How to use `TaskExecutorService` in any Python code
- **Audience**: Developers integrating Ollama tasks
- **Key topics**:
  - Installation (claudeclockwork package)
  - Environment variable setup
  - API: `execute_task()`, `health_check()`, `get_stats()`
  - Escalation levels and model selection
  - Examples for L1, L2, fallback behavior
  - Error handling and troubleshooting

**Start here if you want to USE the Ollama service.**

### [README.md](../README.md)
- **Purpose**: Quick overview of `.ollama` folder
- **Audience**: All developers
- **Key topics**:
  - Folder structure
  - Feature summary
  - Quick start (3 steps)
  - Routing matrix

---

## Operations & Troubleshooting

### [RUNBOOK-001: Ollama Service Failure Recovery](RUNBOOK-001-ollama-service-failure.md)
- **Purpose**: How to diagnose and recover from Ollama outages
- **Audience**: On-call engineers, DevOps, backend leads
- **Key topics**:
  - Detection (automated alerts, manual symptoms)
  - Diagnosis (1-2 minutes)
  - Resolution steps (restart, unload models, cleanup)
  - Verification checklist
  - Escalation procedures
  - Prevention (maintenance, configuration)

**Use this if Ollama is down or misbehaving.**

---

## Testing

### [tests/test_task_executor_service.py](../tests/test_task_executor_service.py)
- **Purpose**: Unit tests for TaskExecutorService
- **Audience**: Developers
- **Coverage**:
  - Input validation (missing prompt, invalid escalation level)
  - Ollama availability and fallback behavior
  - Force Ollama mode (strict, no fallback)
  - Cost tracking (Ollama $0, Claude nonzero)
  - L5 escalation (stop and ask user)
  - Healthy execution flow

**Run with**: `pytest tests/test_task_executor_service.py -v`

---

## Code

### [app/services.py](../app/services.py)
- **Purpose**: Pure Python `TaskExecutorService` adapter
- **No Flask dependency**: Works standalone
- **Key class**: `TaskExecutorService` (singleton)
- **Methods**:
  - `is_available()` — Check if service ready
  - `health_check()` — Ollama and budget status
  - `execute_task()` — Execute with intelligent routing
  - `get_stats()` — Cumulative cost and tokens

---

## Examples

### [examples.py](../examples.py)
- **Purpose**: Runnable examples of all TaskExecutorService features
- **Usage**: `python examples.py [example_name]`
- **Examples**:
  - `health` — Check health status
  - `l1_code_draft` — Code drafting (Ollama)
  - `l2_architecture` — Architecture design (Ollama 72B)
  - `fallback` — Demonstrate fallback to Claude
  - `stats` — Show cost tracking
  - `force_ollama` — Force local-only execution

---

## Configuration

### [.env.example](../.env.example)
- **Purpose**: Environment variables for Ollama integration
- **Key variables**:
  - `ANTHROPIC_API_KEY` — Required for Claude fallback
  - `OLLAMA_HOST` — Ollama server hostname (default: localhost)
  - `OLLAMA_PORT` — Ollama server port (default: 11434)
  - `OLLAMA_FALLBACK_TO_CLAUDE` — Fallback behavior (default: true)
  - `OLLAMA_KEEP_ALIVE` — Model unload timeout (default: 5m)

---

## Decision Tree: Which Document?

```
I want to...
├─ Understand the routing strategy
│  └─ → ADR-004 (Ollama-First Routing Architecture)
├─ Use Ollama in my code
│  └─ → INTEGRATION_GUIDE.md
├─ Diagnose a problem
│  ├─ If Ollama is down → RUNBOOK-001
│  ├─ If costs are high → ADR-003 (budgeting)
│  ├─ If feature broken → Check tests/
│  └─ Otherwise → INTEGRATION_GUIDE.md (Troubleshooting)
├─ Understand cost control
│  └─ → ADR-003 (Token Budgeting)
├─ Set up for the first time
│  └─ → INTEGRATION_GUIDE.md (Installation section)
├─ Run tests
│  └─ → tests/test_task_executor_service.py
└─ See working examples
   └─ → examples.py
```

---

## Quick Reference: Escalation Levels

| Level | Target | Models | Cost | Use Case |
|-------|--------|--------|------|----------|
| **L0** | None | — | $0 | Trivial (1 file, no API change) |
| **L1** | Ollama | qwen2.5-coder:32b | $0 | Code drafting, testing |
| **L2** | Ollama | qwen2.5:72b | $0 | Architecture, modules |
| **L3** | Claude | claude-sonnet-4-6 | ~$0.3 | Performance, API review |
| **L4** | Claude | claude-opus-4-6 | ~$1.5 | Governance, systemic |
| **L5** | Stop | — | N/A | User approval required |

See ADR-004 for full details.

---

## Maintenance Checklist

### Weekly
- [ ] Review error logs for Ollama issues
- [ ] Check disk space on Ollama cache directory
- [ ] Monitor GPU memory usage

### Monthly
- [ ] Test Ollama service recovery (RUNBOOK-001)
- [ ] Review cumulative costs vs budget
- [ ] Update documentation if needed

### Quarterly
- [ ] Review routing decisions vs actual usage
- [ ] Check for new Ollama versions
- [ ] Assess if escalation levels need adjustment

---

## Related Documentation (in other folders)

- `ADR-001`: Tag-based suggestion ranking (uses Ollama routing)
- `ADR-002`: Wiki payload-only suggestions (uses Ollama routing)
- `.clockwork_integration/claudeclockwork/` — Ollama package implementation
- `backend/` — Flask integration (optional)

---

## Contact & Support

- **Questions about routing**: See ADR-004
- **Questions about usage**: See INTEGRATION_GUIDE.md
- **Service is down**: See RUNBOOK-001
- **Testing**: See tests/
- **Examples**: See examples.py
