# Task: Plan Compaction v2

## Goal
Produce a small PlanSpec that complies with Planning Policy.

## Rules
- tasks <= max_plan_tasks (read from `.claude/settings.local.json`)
- constraints <= 5
- each task has <= 5 steps

## Output
- `PlanSpec` JSON file
