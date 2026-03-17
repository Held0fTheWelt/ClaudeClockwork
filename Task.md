You are Claude running inside the ClaudeClockwork repository.

Mission:
Replace the current ad-hoc Ollama briefing script workflow with a canonical reusable skill so Claude does not keep writing one-off Python request scripts for Ollama briefings.

Critical execution rule:
Let Ollama workers implement the work.
Do not do the implementation yourself with Claude-only coding.
Do not stop at analysis.
Do not return only a plan.
Implement the feature in the repo, update docs, add regression coverage, and report changed files and gates.

Project language rule:
All project-facing changes must remain in English.

Context you must respect:
- The repo already contains `.claude/tools/ollama_brief.py`.
- The repo already has a skill runner at `.claude/tools/skills/skill_runner.py`.
- The repo already has a skill directory structure under `.claude/skills/`.
- Recent consolidation work established SSOT-style contracts and boot checks.
- The local canonical Ollama runtime is now native Windows Ollama on `http://127.0.0.1:11434`, GPU-first.
- The practical default local model should be `qwen3:8b`.
- `phi4` should be the lightweight fallback.
- Automatic escalation to 32B/70B/72B local models must not be the default behavior for this path.

Primary goal:
Create a first-class `ollama_briefing` skill that can be invoked through the skill runner, reuses or absorbs the existing `ollama_brief.py` logic, and becomes the canonical path for worker brief generation.

Required outcomes:
1. Introduce a new skill:
   - Skill ID: `ollama_briefing`
   - Add `.claude/skills/ollama_briefing/SKILL.md`
   - Add a manifest if the current repo conventions now support manifests
   - The skill description must clearly say it should be used whenever Claude needs an Ollama-generated brief, draft, architecture note, review, or quick assessment instead of writing a fresh request script

2. Add a deterministic skill implementation:
   - Add `.claude/tools/skills/ollama_briefing.py`
   - It must expose `run(request: dict) -> dict`
   - It must work through the existing skill runner
   - It must produce a proper SkillResultSpec-style result
   - It must not rely on hand-edited temporary scripts

3. Canonicalize existing ad-hoc logic:
   - Reuse `.claude/tools/ollama_brief.py` logic where appropriate, but do not leave two competing sources of truth
   - Either:
     - refactor shared Ollama briefing logic into a common helper module used by both paths, or
     - make `ollama_brief.py` a thin compatibility wrapper around the canonical skill/backend
   - The canonical behavior must live in the new skill path, not only in the old script

4. Support these task modes:
   - `brief`
   - `draft`
   - `architecture`
   - `review`
   - `quick`

5. Inputs contract:
   The skill must accept inputs like:
   - `prompt` or `task`
   - `task_type`
   - `model` (optional)
   - `base_url` (optional)
   - `timeout_seconds` (optional)
   - `num_ctx` (optional)
   - `num_predict` (optional)
   - `temperature` (optional)
   - `write_output_path` (optional)
   - `metadata` (optional)

6. Runtime policy:
   - Default base URL must be `http://127.0.0.1:11434`
   - Default model must be `qwen3:8b`
   - Fallback model must be `phi4`
   - Default `num_ctx` should be `4096`
   - Must not default to old CPU-heavy models like `qwen2.5-coder:32b`
   - Must not silently escalate to 32B/70B/72B models
   - Connection failures must fail clearly and report degraded/Ollama-unavailable state
   - Do not silently succeed with fake output

7. Output contract:
   Return structured results containing at minimum:
   - `status`
   - `skill_id`
   - `request_id`
   - `model`
   - `task_type`
   - `content`
   - `base_url`
   - `timeout_seconds`
   - optional file output metadata when `write_output_path` is used
   - clear error details on failure

8. Skill runner integration:
   - Register the new skill in `.claude/tools/skills/skill_runner.py`
   - Ensure it can be invoked with a normal skill request JSON
   - Do not break existing skills

9. Documentation:
   Update the relevant docs so this becomes the recommended path instead of ad-hoc request scripts:
   - `.claude/skills/QUICKSTART.md`
   - `.claude/governance/ollama_integration.md`
   - `.claude/tools/README.md`
   - `.claude/CHANGELOG.md`
   - Any registry/index file that should mention the new skill

10. Tests and gates:
   Add regression coverage for:
   - skill registration
   - valid request handling
   - default model/base URL behavior
   - task type mapping
   - output schema shape
   - Ollama unavailable failure path
   - optional write-to-file behavior
   - compatibility behavior of the old `ollama_brief.py` path if retained
   Run the relevant test subset and the boot/gate checks and report results.

Implementation constraints:
- Keep project-facing wording in English
- Prefer small focused modules
- No circular imports
- No duplicate logic islands
- No throwaway scripts committed as the feature
- No documentation-only completion
- Do not weaken the runtime policy just to make tests pass

Concrete acceptance criteria:
- A user can invoke `ollama_briefing` through the skill runner with a SkillRequestSpec
- The skill produces a structured result using the local Windows Ollama backend
- The default route uses `qwen3:8b`
- The old ad-hoc script path is either deprecated into a thin wrapper or clearly made subordinate to the canonical skill implementation
- Docs point users toward the skill instead of new one-off scripts
- Tests pass
- Boot/gate checks pass

Suggested example request to support:
{
  "type": "skill_request_spec",
  "request_id": "req-ollama-brief-001",
  "skill_id": "ollama_briefing",
  "inputs": {
    "task_type": "brief",
    "prompt": "Analyze the next consolidation wave for the skill system and list implementation steps.",
    "model": "qwen3:8b",
    "timeout_seconds": 300
  }
}

At the end, report:
- changed files
- tests run
- gate/boot-check results
- whether `ollama_brief.py` remains as a wrapper or was refactored
- any follow-up drift still remaining