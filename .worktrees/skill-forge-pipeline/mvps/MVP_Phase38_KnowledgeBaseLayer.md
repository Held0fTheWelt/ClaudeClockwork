# MVP Phase 38 — Knowledge Base Layer (Project Index + Retrieval)

**Goal:** Add a local knowledge base per project/workspace: index docs/manifests/contracts and provide retrieval tools (with citations to repo paths) to keep context small and answers grounded.

**Why now:** After many phases, you need fast answers like “which policy applies?”, “which MVP owns this?”, “where is this contract defined?” without scanning manually.

---

## Definition of Done

- [x] Project indexer exists (docs, manifests, contracts, runbooks)
- [x] Local embeddings + vector index exist (per project) OR keyword index fallback
- [x] Query tools exist:
  - `kb.search`
  - `kb.explain` (returns citations to files/paths)
- [x] Index updates are incremental and deterministic
- [x] Governance: indexer respects boundaries and ignores runtime artifacts by default
- [x] Tests cover indexing + retrieval determinism
- [x] All existing tests pass

---

## K38.1 — Index Scope + Rules

**Files:**
- `Docs/kb_scope.md` (new)
- `claudeclockwork/kb/scope.py` (new)

**Change:**
- Include:
  - `Docs/`, `mvps/`, `.claude/skills/**/manifest.json`, `.claude/contracts/`
- Exclude:
  - runtime root
  - `__pycache__`, venvs, build artifacts
- Respect workspace boundaries.

**Acceptance:**
- Index scope is stable and documented.

---

## K38.2 — Indexer + Storage

**Files:**
- `claudeclockwork/kb/indexer.py`
- `claudeclockwork/kb/store.py`
- `tests/test_kb_indexer.py`

**Change:**
- Store:
  - doc id
  - path
  - content hash
  - extracted metadata (title, headings)
- Incremental updates by hash.

**Acceptance:**
- Re-indexing without changes produces no diffs.

---

## K38.3 — Retrieval (Embeddings or Keyword Fallback)

**Files:**
- `claudeclockwork/kb/retrieval.py`
- `Docs/kb_retrieval.md` (new)

**Change:**
- Prefer local embeddings via LocalAI (Phase 20) if available.
- Fallback to keyword + BM25-like scoring if embeddings unavailable.

**Acceptance:**
- Retrieval returns deterministic ranked results for a given query.

---

## K38.4 — Query Tools with Citations

**Files:**
- `.claude/skills/kb/search/manifest.json` (+ `skill.py`)
- `.claude/skills/kb/explain/manifest.json` (+ `skill.py`)
- `tests/test_kb_skills.py`

**Change:**
- `kb.search` returns a list of objects like: `{"path": "...", "snippet": "...", "score": 0.0}`.
- `kb.explain` returns an answer plus explicit file path citations.

**Acceptance:**
- Tools never cite runtime artifacts by default.
- Output includes stable, repo-local citations.

---
