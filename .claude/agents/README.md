# Agent Layer — Index (CCW-MVP03)

_Last updated: 2026-03-02. Scope: `.claude/agents/` — do not modify existing agent files._

---

## Role Overview Table

| Role | File | Escalation Level | Output Format |
|---|---|---|---|
| TeamLead | `team_lead.md` | Orchestrator | Markdown (Task Brief) |
| Implementation Worker | `workers/implementation_worker.md` | L0–L1 | JSON |
| Personaler (Router) | `personaler.md` | L1+ pre-dispatch | JSON (RoutingSpec) |
| Tester (Smoke) | `tester.md` | L1+ post-build | JSON + Markdown report |
| Librarian | `librarian.md` | L0–L1 support | Markdown (DocPack) |
| Critic — Technical | `critics/technical.md` | L3 mandatory | Markdown (Audit) |
| Critic — Systemic | `critics/systemic.md` | L4 mandatory | Markdown (Audit) |

Additional roles (see subdirectories): `critics/`, `workers/`, `docs/`, `analysis/`,
`operations/`, `testops/`, `quality/`, `meta/`, `learning/`.

---

## Orchestration Standard

```
User trigger
  └─► TeamLead (parse + classify)
        ├─► Personaler  → RoutingSpec (model, tier, trust)
        ├─► Implementation Worker  → JSON result
        ├─► Tester  → pass / warn / fail
        ├─► [Critic-Technical]  → L3 mandatory, L2 optional
        ├─► [Critic-Systemic]   → L4 mandatory
        └─► Librarian  → DocPack (context support, any level)
```

**Call chain rules:**
- TeamLead delegates via Task-Tool; never writes code directly.
- Personaler is called *before* any Ollama/Claude Worker at L1+.
- Tester runs *after* build, *before* Review/Docs phase.
- Critics are called by TeamLead on threshold breach; never self-activate.
- Librarian is a support role — any agent may request a DocPack.

---

## Output Format

| Role | Format | Destination |
|---|---|---|
| TeamLead | Markdown Task Brief | `Docs/Plans/` |
| Implementation Worker | JSON `{status, changed_files, notes, rerun_tests}` | returned to TeamLead |
| Personaler | JSON RoutingSpec | returned to TeamLead / orchestrator |
| Tester | JSON `{status, action, checks, findings}` + optional `.md` | `Docs/Review/` |
| Librarian | Markdown DocPack (paths + relevance) | returned inline |
| Critic — Technical | Markdown Audit (Findings + Recommendation) | `Docs/Audits/` |
| Critic — Systemic | Markdown Audit (Findings + Recommendation) | `Docs/Audits/` |

---

## Model Policy

- **Haiku (C1):** administrative dispatch, Task Compaction, brief reviews, fast triage.
- **Sonnet (C2/C3):** planning, architecture audits, precise implementation/debug, Critic reviews.
- **Opus (C4):** disabled by default — only on explicit manual opt-in for deep review.
- **Local-first:** prefer Oodle Tier S→M→L before escalating to Claude (see `governance/model_escalation_policy.md`).

---

## Local Ollama Models

**See:** `docs/ollama_model_guide.md` for comprehensive usage guide on qwen3.5-35b:agent and other local models.

### qwen3.5-35b:agent Summary
- **Cost:** $0 (local)
- **Speed:** 20-35 min per batch
- **Quality:** Excellent for code analysis (11/11 audit defects detected; 2 critical security issues found)
- **Best for:** Code audits, defect detection, security reviews, multi-file analysis
- **Context:** 4096 tokens (batch inputs to 2500 tokens for safe response buffer)
