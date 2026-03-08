# MVP Phase 65 — Runtime Root Cleanup & Anti-Coupling Gate (`.llama_runtime`)

**Goal:** Remove or fully deprecate `.llama_runtime/` within ClaudeClockwork and enforce `.clockwork_runtime/` as the only active runtime root.

**Observed (repo scan 2026-03-08):**
- `.llama_runtime/` still exists with many artifacts.

---

## Definition of Done

- [x] ✅ `.llama_runtime/` is removed OR replaced with a tiny legacy stub (README + .gitkeep)
- [x] ✅ All runtime writes go to `.clockwork_runtime/`
- [x] ✅ A gate blocks reintroducing `.llama_runtime/` usage
- [x] ✅ References to `.llama_runtime/` removed from docs/code/tests (except legacy note)
- [x] ✅ All existing tests pass

---

## C65.1 — Inventory + Migration

**Files:**
- `.llama_runtime/**`
- `.clockwork_runtime/**`

**Change:**
- Inventory and decide what to migrate vs discard.

**Acceptance:**
- `Docs/runtime_migration_llama_to_clockwork.md` documents outcomes.

---

## C65.2 — Remove / Stub

**Change:**
- Remove `.llama_runtime` OR keep only README+.gitkeep legacy stub.

**Acceptance:**
- No active artifacts remain under `.llama_runtime`.

---

## C65.3 — Anti-Coupling Gate

**Files:**
- `claudeclockwork/core/gates/runtime_root_gate.py` (new)
- `tests/test_runtime_root_gate.py`

**Change:**
- Gate fails if `.llama_runtime` contains non-stub files or if code/docs reference it.

**Acceptance:**
- Synthetic reintroduction fails deterministically.

---
