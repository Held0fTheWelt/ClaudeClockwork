# Remote Worker Stub (Phase 35)

- Remote worker can be contacted via HTTP (POST envelope, return result), WebSocket, or CLI (stdin envelope, stdout result).
- MVP keeps actual networking minimal; focus on protocol correctness (envelope schema, idempotency_key, artifact refs).
- Optional: `claudeclockwork/workers/http_worker_client.py` as stub for future HTTP client.
