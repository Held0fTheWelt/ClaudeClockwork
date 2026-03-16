# ClaudeClockwork local Ollama mode

This document explains the revised `ollama_setup.py` and the companion `wsl_setup.sh` for **ClaudeClockwork**.

It is meant to be readable first, editable second, and safe to adopt incrementally.

---

## Why this revision exists

The previous setup already had strong ideas:

- profile-based Ollama aliases
- a swarm-style role pipeline
- separate profiles for coding, review, planning, docs, and creativity
- a WSL environment optimized for large local models

But it also had a few weak points that matter in daily Clockwork work:

1. **Too much was destructive by default**
   - model deletion was part of the normal flow
   - this makes experimentation unnecessarily risky

2. **The temporary modelfile path was not WSL-safe enough**
   - Windows-style temp fallbacks are a poor fit inside WSL

3. **Host binding was not explicit enough**
   - that makes Windows ↔ WSL access harder to reason about

4. **The role model was more “generic swarm” than “ClaudeClockwork”**
   - ClaudeClockwork already has a real agent system, policies, routing, escalation, critics, documentation flows, and pack workflows
   - the local Ollama mode should therefore mirror Clockwork roles more directly

This revision fixes those issues without throwing away the good parts.

---

## Design goals

The revised mode is built around five rules:

### 1. Quality first

This setup assumes that **better answers matter more than raw speed**.

That means:

- large 32B / 70B / 72B models remain welcome
- some roles are intentionally slow if they are used only for the highest-value decisions
- small models still exist, but mainly for packing, docs, and fast summaries

### 2. Safe by default

The revised `ollama_setup.py` does **not**:

- delete models automatically
- pull huge missing models automatically
- overwrite repo policy files

Those actions are opt-in.

### 3. Clockwork-aligned roles

The setup is no longer just “planner / coder / reviewer / summarizer”.
It now reflects how ClaudeClockwork actually works.

Important roles in the revised mode include:

- `team_lead_orchestrator`
- `designer_planner`
- `context_packer`
- `task_compactor`
- `implementation_worker`
- `unreal_specialist`
- `integrator`
- `reviewer_primary`
- `reviewer_crosscheck`
- `arbiter`
- `failure_autopsy`
- `documentation_worker`
- `release_notes_editor`
- `research_fast`
- `research_heavy`
- `creative_primary`
- `vision_review`
- `embedding_primary`

### 4. Repo policy remains the source of truth

This local mode is a **companion** to the Clockwork repo, not a replacement for it.

It should sit beside the repo’s own governance and routing files.

### 5. Easy to revise

The generated config is written to:

```text
~/.claudeclockwork/ollama/clockwork_mode.json
```

So you can iterate on the local mode without mutating core repo policy files every time.

---

## How this fits ClaudeClockwork

ClaudeClockwork already distinguishes between:

- strategic orchestration
- planners and packers
- implementation workers
- critics and review gates
- documentation and release flows
- external routing / escalation policy

The local Ollama mode now maps onto that more cleanly.

### Strategic layer

Use larger reasoning models for:

- orchestration
- escalations
- difficult trade-offs
- major planning packets

Default candidates:

- `llama3.3-70b:reasoning`
- `qwen2.5-72b:reasoning`
- `qwen2.5-72b:planning`

### Worker layer

Use strong coders for:

- implementation
- Unreal work
- multi-file integration

Default candidates:

- `qwen2.5-coder-32b:coding`
- `qwen2.5-coder-32b:unreal`
- `qwen2.5-coder-32b:integration`
- `deepseek-coder-33b:coding`

### Review layer

Use an intentionally separate review path:

- `deepseek-coder-33b:review`
- `qwen2.5-coder-32b:review`

This is important because Clockwork benefits from **independent review signals**, not just self-review by the same implementation model.

### Arbitration and failure analysis

These are new high-leverage additions.

They matter because Clockwork already has critics, escalation, and evidence-based review patterns.

Optional candidates:

- `deepseek-r1-14b:judge`
- `deepseek-r1-14b:autopsy`

### Pack / summary layer

These roles are often more valuable than yet another big coding model.

They reduce noise and keep context windows usable.

Default candidates:

- `qwen2.5-14b:packing`
- `qwen2.5-14b:summarize`
- `qwen2.5-14b:docs`

---

## Stable model set vs optional expansion

The revised Python script is split into two groups.

## Stable recipes

These are the aliases that make sense for the workstation you are already using and for the models you likely already keep around:

- `qwen2.5-coder:32b`
- `deepseek-coder:33b-instruct-q4_K_M`
- `qwen2.5:14b-instruct`
- `qwen2.5:72b-instruct-q5_K_M`
- `llama3.3:70b-instruct-q5_K_M`

These cover the core Clockwork workflow well.

## Optional recipes

These are for the next wave of specialization:

- `qwen3-coder:30b`
- `devstral-small-2`
- `deepseek-r1:14b`
- `gemma3:12b`

These are intentionally optional because they are role-expanding models, not baseline requirements.

---

## New profile structure

The revised setup keeps profile tuning, but it reorganizes it around clearer Clockwork jobs.

### Core profiles

- `execution`
- `coding`
- `unreal`
- `review`
- `planning`
- `reasoning`
- `integration`
- `docs`
- `summarize`
- `packing`
- `research`
- `creative`

### New high-value specialist profiles

- `judge`
- `autopsy`
- `vision`

These three profiles are what most clearly turn the setup from a generic swarm into a Clockwork-ready local operating mode.

---

## Why the WSL script was revised too

The updated `wsl_setup.sh` is not just cosmetic.

It fixes three operational gaps:

### 1. Explicit `OLLAMA_HOST`

The script now writes:

```text
OLLAMA_HOST=0.0.0.0:11434
```

by default, unless you choose `--local-only`.

That makes Windows ↔ WSL access behavior explicit and predictable.

### 2. Explicit systemd service environment

The service file now includes the important runtime variables directly, including:

- `GGML_CUDA_NO_PINNED=1`
- `OLLAMA_MODELS=...`
- `OLLAMA_LOAD_TIMEOUT=...`
- `OLLAMA_FLASH_ATTENTION=1`
- `OLLAMA_NUM_THREADS=...`
- `OLLAMA_NUM_PARALLEL=1`
- `OLLAMA_KEEP_ALIVE=30m`
- `OLLAMA_HOST=...`

That means the service behavior is easier to inspect and much less dependent on shell state.

### 3. Safer workstation guidance

The script keeps mounted Windows model storage valid, but makes the trade-off clearer:

- it works
- it can be slower for large models
- it is not a correctness problem

---

## Recommended operating pattern

Use the setup in three passes.

### Pass 1: verify environment

```bash
bash wsl_setup.sh --check
python ollama_setup.py --check
```

### Pass 2: inspect the local role map

```bash
python ollama_setup.py --summary
python ollama_setup.py --list-profiles
python ollama_setup.py --list-roles
```

### Pass 3: build the baseline aliases

```bash
python ollama_setup.py
```

### Pass 4: extend into special roles later

```bash
python ollama_setup.py --with-optional
```

### Pull missing source models only when you actually want them

```bash
python ollama_setup.py --with-optional --pull-missing
```

---

## What changed conceptually

The most important conceptual change is this:

**The local Ollama setup is no longer treated as a generic model farm.**
It is treated as a **Clockwork operating mode**.

That means model aliases now exist for real Clockwork jobs such as:

- pack building
- integration
- arbitration
- autopsy
- Unreal specialization
- release-note and documentation support

This is the main reason the revision is easier to understand and easier to extend.

---

## What to revise first if you customize it

If you want to adapt the mode, the highest-value edit points are:

### 1. `CLOCKWORK_MODE["roles"]`

This is the most important table.

That is where you decide which local alias should serve each Clockwork responsibility.

### 2. `MODEL_RECIPES`

Edit this when:

- you replace a base model
- you want a different alias structure
- you want a narrower or broader baseline

### 3. `OPTIONAL_RECIPES`

Edit this when:

- you test new specialist models
- you want more experimental roles
- you add a second vision or judge path

### 4. `PROFILES`

Edit this when:

- you want different context limits
- you want more or less creativity
- you need stricter deterministic behavior for a role

### 5. `wsl_setup.sh`

Edit this when:

- you move the models path
- you change RAM or swap
- you want local-only instead of external bind
- you want different keep-alive or timeout behavior

---

## Suggested next specializations for ClaudeClockwork

If you keep evolving the mode, these are the most useful next task classes to formalize:

1. **Arbiter / Judge**
   - resolves disagreement between reviewer paths

2. **Failure Autopsy**
   - turns failed runs into explicit first-cause analysis

3. **Pack Compactor**
   - compresses large task briefs into execution-safe packets

4. **Repo Operator**
   - tuned for large codebase navigation and multi-file edits

5. **Unreal Specialist**
   - tuned for engine-source, plugin, editor, and packaging work

6. **Release Steward**
   - changelog, migrations, breakage notes, upgrade guidance

7. **Lore / Brand Guard**
   - useful for World of Shadows and other narrative-heavy work

---

## Bottom line

The revised setup is built around a simple principle:

> **Use local Ollama models as a Clockwork-specific worker stack, not just a bag of models.**

That gives you:

- clearer role ownership
- safer defaults
- easier iteration
- better alignment with the actual ClaudeClockwork repo
- a more useful path for future specialization
