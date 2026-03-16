# Collaboration Guide — Python Orchestrator Agent System

> Scenario-specific recommendations for team composition and workload balancing.
> Managed by the Skill Agent. Reference for Team Lead in orchestration decisions.

---

## When to Assemble Which Team?

### Scenario A: Implement New Python Function/Class

```
Ollama: qwen2.5-coder:32b / draft
Implementation Agent: sonnet
Collector: haiku (only if >100 lines or external module dependency)
Validation: only if subprocess handling or Ollama client change
```

No Architecture Agent, no Critics needed — unless module boundary decision is unclear.

---

### Scenario B: Python Architecture Decision (New Module vs. Extension?)

```
Ollama: phi4:14b / architecture
Architecture Agent (Designer): sonnet
Team Lead: Decision after architecture feedback
```

No Specialist needed until decision is made.

---

### Scenario C: Bugfix (Single-File, Clearly Isolated)

```
No Ollama (L0)
Appropriate Specialist: haiku
No QA
```

Fastest possible execution — no overhead.

---

### Scenario D: Team Efficiency Analysis

```
Ollama: phi4:14b / architecture (system analysis as basis)
Skill Agent: sonnet
Input: Ollama briefing + last 3-5 tasks + routing.md + learning logs
Output: Recommendation for Team Lead (collaboration.md update)
```

Team Lead consults Skill Agent when: same task type fails repeatedly, costs unexpectedly high, new task class appears.

---

### Scenario E: Critical Review (L3+)

```
Ollama: phi4:14b / architecture (preliminary analysis)
Technical Critic: sonnet
Systemic Critic: sonnet (only for L4)
Team Lead: Decision after critic inputs
```

Critics run in parallel. Team Lead waits for both before deciding.

---

### Scenario F: Documentation After Implementation (Phase 4a)

```
No Ollama
Documentation Agent: haiku
Librarian Agent: haiku (index update)
```

Can run in parallel. No QA needed. Automatically triggers Scenario J (Phase 4b).

---

### Scenario G: Information Request (Agent Needs Context)

```
Specialist → Team Lead: "I need knowledge about [topic]"
Librarian: haiku (single file) or sonnet (multi-file)
Ollama: qwen2.5-coder:14b/quick or qwen2.5-coder:32b/brief
Output: File paths + extracted key passages
→ Team Lead passes information package to Specialist
```

No Specialist searches files themselves — always via Librarian.

---

### Scenario H: Parallel Librarian Requests (Collective)

```
2+ Specialists need information simultaneously:
Team Lead → 2x Librarian (haiku, parallel via Task tool)
Each Librarian serves one requester
Results are delivered in parallel
```

Saves time — no sequential waiting for the Librarian.

---

### Scenario I: Domain Handoff (Orchestrator Needs Ollama Client Change)

```
Implementation Agent recognizes: "I need a change in ollama_client.py"
Implementation Agent → Team Lead: Report
Team Lead → Architecture Agent: Module boundary decision
Architecture Agent → Team Lead: Decision + specification
Team Lead → Implementation Agent: Specification as context
Implementation Agent: Implements with this context
```

No silent takeover — formal handoff via Team Lead.

---

### Scenario J: Human-Facing Docs QA (Phase 4b)

```
Ollama: phi4:14b / architecture (for both agents before start)
Human Readable Document Agent: sonnet
Tutor Agent: sonnet (only when technical content → readable prose, i.e., Docs/Tutorials/)
```

**Trigger:** Automatically after Phase 4a (Scenario F) when output is intended for human readers.

---

### Scenario K: Integrate New Agent (Governance Trinity Update)

```
Ollama: None (project-specific)
Implementation Agent: sonnet (all three Trinity files)
Systemic Critic: sonnet (if L4 — new governance rule)
```

**Critical:** Never partial updates. `specialists.md` + `execution_protocol.md` + `MEMORY.md` are an inseparable unit.

---

## Warning Signs — When to Involve Skill Agent?

| Signal | Cause | Recommendation |
|---|---|---|
| Same task type fails 2x | Wrong routing | Have Skill Agent analyze |
| Haiku produces unusable outputs | Task was L1, not L0 | Adjust model threshold |
| Validation always finds same errors | Specialist learning log outdated | Skill Agent + Pattern Recognition |
| Team Lead unsure which team | New task type | Skill Agent for initial assessment |
| Governance file was changed in isolation | Trinity rule violated | Immediately follow up with Trinity update |

---

## Resource Rules of Thumb

| Situation | Cost Level | Team |
|---|---|---|
| L0 bugfix | Minimal | 1x haiku |
| L1 implementation | Low | 1x sonnet + Ollama |
| L2 architecture | Medium | Ollama + Architecture Agent + possibly Specialist |
| L3 review | High | Ollama + Specialist + Critics |
| Governance Trinity update | Low-Medium | 1x sonnet (Implementation Agent) |
| Human-Facing Docs QA (Phase 4b) | Low | 1-2x sonnet (parallel) |
| Efficiency analysis | One-time | Skill Agent (sonnet) |

## Operational Defaults (v17.x)

- **German narrative input**: Build a **Message Triad** first (`MessageTriadSpec`), then work from `work_brief`.
- **Fallback order**: work_brief → translation → source (original).
- **Hard STOP**: If Drift Sentinel FAILs, stop and fix drift before proceeding.
- **Policy**: Use `policy_gatekeeper` to decide if deep_oodle / creative_feedback / rebuild / experiments are allowed.
- **Deep reasoning**: Only use Deep Oodle with a Deliberation Pack built by `deliberation_pack_build`.
