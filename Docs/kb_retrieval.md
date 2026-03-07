# KB Retrieval (Phase 38)

- Prefer local embeddings (LocalAI) if available; fallback to keyword + BM25-like scoring.
- Retrieval returns deterministic ranked results for a given query. kb.search and kb.explain return repo-local citations.
