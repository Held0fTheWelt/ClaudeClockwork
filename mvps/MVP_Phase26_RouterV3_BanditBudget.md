# MVP Phase 26 — Router v3 (Bandit + Budget Toggle, End-to-End)

**Goal:** Implement an end-to-end router that chooses between:
- LLM models (e.g. “fast” vs “strong”)
- LocalAI tools vs LLM reasoning
- Tool variants (CPU/GPU, model sizes)
based on task features, budget, and learned success profiles.

**Why now:** After Phase 25 (scoreboards), you can train routing decisions on evidence and block regressions.

---

## Definition of Done

- [ ] Router v3 supports multi-armed bandit selection for model/tool choices
- [ ] Budget toggle exists (fast/cheap vs strong/accurate) and affects decisions deterministically
- [ ] Feature extraction exists (task size, modality, risk)
- [ ] Feedback loop updates profiles from eval + manual rating
- [ ] Router decisions are explainable (returns a rationale payload)
- [ ] All existing tests pass

---

## R26.1 — Decision Graph + Rationale Contract

**Files:**
- `Docs/router_v3_contract.md` (new)
- `claudeclockwork/router/contracts.py`

**Change:**
- Define router output:
  - chosen option
  - alternatives considered
  - reason codes (budget, latency, quality, safety)
  - confidence / expected cost

**Acceptance:**
- Router always returns a contract-compliant rationale.

---

## R26.2 — Bandit Policy + Profiles

**Files:**
- `claudeclockwork/router/bandit.py`
- `claudeclockwork/router/profiles_store.py`
- `tests/test_router_bandit.py`

**Change:**
- Thompson Sampling preferred; fallback epsilon-greedy.
- Profiles stored under runtime root (JSONL + snapshot).
- Cold-start behavior defined (safe defaults).

**Acceptance:**
- Deterministic seed option yields reproducible choices in tests.

---

## R26.3 — Budget Toggle + Safety Constraints

**Files:**
- Router config (existing)
- Capability policy (Phase 24)

**Change:**
- Budget levels: `fast`, `balanced`, `strong`
- Safety constraints override budget (e.g. disallow risky tools or untrusted runners).

**Acceptance:**
- Safety blocks cannot be bypassed by budget setting.

---

## R26.4 — End-to-End Eval Integration

**Files:**
- Eval harness (Phase 25)
- Router modules

**Change:**
- Router v3 evaluated on golden suites:
  - score impact (quality/latency)
  - stability (low variance)
  - failure behavior (fallbacks)

**Acceptance:**
- Scoreboard shows router performance per budget profile.

---
