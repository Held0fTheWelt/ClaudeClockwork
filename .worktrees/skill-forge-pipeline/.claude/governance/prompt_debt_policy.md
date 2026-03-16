# Prompt Debt Policy

Prompt debt is accumulated when a task fails repeatedly due to unclear prompts/contracts,
not due to code complexity.

## When to create a PromptDebtItem
- Same failure mode repeats >= 2 times
- Agent drift occurs (agent leaves scope)
- Spec/contract mismatch recurs

## What a PromptDebtItem contains
- symptom (what happened)
- reproduction steps (minimal)
- suspected root cause (contract missing field / ambiguous instruction)
- proposed fix (schema update / task template / skill)

## Cost control
- Max 5 items per run
- Prefer tool-first checks and schema fixes over adding new agents
