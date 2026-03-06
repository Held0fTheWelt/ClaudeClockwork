# Knowledge Architecture

## Knowledge Taxonomy

All knowledge in the system is classified into three types:

| Type | Location | Lifespan |
|---|---|---|
| **Task Knowledge** | `Docs/Tasks/`, `Docs/Plans/` | Task duration |
| **Reference Knowledge** | `Docs/References/` | Project duration |
| **System Knowledge** | `.claude/` | Permanent |

---

## Indexing Rules

```
- Every entry: tagged by subsystem (Orchestration, Ollama, Claude-API, Workflow, Config, ...)
- Linked by dependencies (e.g., Orchestrator → OllamaClient → Config)
- Prioritized by usage frequency (frequently referenced patterns → .claude/python/patterns.md)
```

---

## Librarian Responsibilities

| Task | Frequency | Trigger |
|---|---|---|
| Detect redundancy + merge | Post-task | When 2+ similar entries exist |
| Mark outdated entries | Periodically | After API change or module restructuring |
| Maintain cross-references | Post-task | When new system documented |
| Optimize retrieval paths | Quarterly | On knowledge bloat warning |

---

## Knowledge Flow

```
Implementation
    ↓ (Pattern Recognition Agent)
Patterns identified
    ↓ (Librarian Agent)
.claude/python/patterns.md OR Docs/References/
    ↓ (Documentation Agent)
Docs/Documentation/ (detailed technical documentation)
    ↓ (MEMORY.md Update)
Stable insights in MEMORY.md
```

---

## Retrieval Strategy

When an agent searches for knowledge, they follow this order:

1. **MEMORY.md** — stable, frequently needed insights
2. **`.claude/python/patterns.md`** — project-specific Python patterns
3. **`Docs/References/`** — detailed system references
4. **`Docs/Documentation/`** — technical implementation details
5. **Source code directly** — if no documentation available

---

## Knowledge Subsystem Tags

| Tag | Description |
|---|---|
| `Orchestration` | `<PROJECT_ROOT>/src/orchestrator.py` — Task routing, classification |
| `Ollama` | `<PROJECT_ROOT>/src/ollama_client.py` — LLM inference, freeze protocol |
| `Claude-API` | `<PROJECT_ROOT>/src/claude_client.py` — Subagent spawning |
| `Workflow` | `<PROJECT_ROOT>/src/workflow.py` — Trigger recognition, doc naming |
| `Config` | `<PROJECT_ROOT>/src/config.py` — Paths, models, constants |
| `Agents` | `<PROJECT_ROOT>/src/agents/` — Specialist implementations |
| `Governance` | `.claude/governance/` — Process rules |
| `Architecture` | `.claude/python/architecture.md` — Module hierarchy |
| `Patterns` | `.claude/python/patterns.md` — Reusable patterns |

---

## Quality Thresholds

A knowledge entry is marked as **outdated** when:
- 3+ months since last usage
- Module it describes was restructured
- API it describes was changed

A knowledge entry is **deleted** when:
- Marked as outdated + no update in 30 days
- Completely covered by another entry
- Describes a system that no longer exists
