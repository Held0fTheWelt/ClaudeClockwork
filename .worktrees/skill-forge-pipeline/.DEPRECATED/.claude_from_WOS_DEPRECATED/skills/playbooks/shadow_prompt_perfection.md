# Shadow Prompt Perfection Playbook (Ollama + Optional Sonnet/Opus)

Purpose: turn an already-good `.claude` prompt set into a **shorter** and **more instruction-dense** variant, while keeping correctness.

## Roles (recommended)
1) **Explore** (cheap): identify redundancy, extract invariants, list "must keep" rules.
2) **Write** (strong): rewrite into minimal instruction sets per file type.
3) **Critic** (strict): try to break the prompts; find ambiguity and missing constraints.
4) **DecideGap** (best judge): assign a gap score and concrete patch list.

## Evaluation strategy
- Default judge: a strong local model (your "Oodle AI" equivalent).
- Escalation:
  - Sonnet only if judge reports persistent ambiguity
  - Opus only if you're optimizing for near-perfect instruction density

## Artifacts
- `.claude_shadow/*.md` (final)
- `shadow_prompt_report.json` with:
  - score_0_100
  - biggest_gaps
  - next_actions
