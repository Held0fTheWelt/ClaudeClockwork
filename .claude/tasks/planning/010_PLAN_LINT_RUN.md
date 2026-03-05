# Task: Run Plan Lint

## Goal
Validate a PlanSpec deterministically.

## How
Use the skill runner with skill_id `plan_lint`.

Example request:
{
  "type": "skill_request_spec",
  "request_id": "req-planlint-001",
  "skill_id": "plan_lint",
  "inputs": {"plan": "path/to/plan.json"}
}

Expected:
- status=ok if plan meets max_plan_tasks and required fields
- status=fail otherwise
