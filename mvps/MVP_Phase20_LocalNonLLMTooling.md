# MVP Phase 20 — Local Non-LLM Tooling (LocalAI) v1

**Goal:** Add a deterministic “local non-LLM tooling layer” to Clockwork: vision/audio/embedding tools executed locally via a stable tool contract, registry, and thin skill wrappers. This is repo-local and independent of LlamaCode.

**Context (repo scan 2026-03-07):**
- Clockwork already has routing/telemetry infrastructure that can evaluate tool performance.
- There is no unified local non-LLM tool contract or registry yet.

---

## Definition of Done

- [ ] Tool contract schema added (JSON Schema): `local_tool_result.schema.json`
- [ ] Model/tool registry format added (YAML/JSON): `localai_registry.yaml`
- [ ] Minimal local runtime implemented (native Python module + optional CLI wrapper)
- [ ] At least 2 capabilities wired end-to-end:
  - `embed.text` (local embeddings)
  - `audio.asr` (local speech-to-text)
  *(Vision optional as third capability)*
- [ ] Thin manifest skills added under `.claude/skills/localai/*` with native implementations
- [ ] Deterministic failure mode: if a tool dependency is missing, return a structured error (no crash)
- [ ] Minimal tests added (mocked runners): contract validation + “missing dependency returns structured error”
- [ ] All existing tests pass

---

## L20.1 — Tool Contract + Registry

**Files:**
- `.claude/contracts/schemas/local_tool_result.schema.json`
- `claudeclockwork/localai/registry.py`
- `claudeclockwork/localai/contracts.py`

**Change:**
Define a stable response shape:
- `capability`, `tool_id`/`model_id`
- `inputs` (paths/params), `outputs` (json + artifact paths)
- `metrics` (latency, device), `errors` (typed)

**Acceptance:**
- Contract validates example outputs for both success and missing-dependency failure.

---

## L20.2 — Local Runtime (Pluggable Runners)

**Files:**
- `claudeclockwork/localai/runtime.py`
- `claudeclockwork/localai/runners/*`

**Change:**
Implement runner abstraction:
- `ExternalCommandRunner` (calls local binaries if installed)
- `PythonRunner` (optional, if dependencies installed)

**Acceptance:**
- Running a capability with an unavailable runner returns:
  - `status: error`
  - `errors: [{code: "dependency_missing", ...}]`

---

## L20.3 — Skills (Thin Wrappers)

**Files:**
- `.claude/skills/localai/localai_run/manifest.json` (+ `skill.py`)
- `.claude/skills/localai/embed_text/manifest.json` (+ `skill.py`)
- `.claude/skills/localai/audio_asr/manifest.json` (+ `skill.py`)

**Change:**
Skills validate inputs, call runtime, return contract-compliant output.

**Acceptance:**
- Skills are discoverable by registry.
- Calls are deterministic with mocked tests (no real weights required).

---

## L20.4 — Minimal Eval Hooks (Optional but recommended)

**Files:**
- `tests/test_localai_contract.py`
- `tests/test_localai_missing_dependency.py`

**Change:**
Add a tiny golden test harness:
- contract validation
- consistent metrics keys

**Acceptance:**
- Tests pass without requiring real model weights.

---
