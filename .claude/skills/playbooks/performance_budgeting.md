# Performance Budgeting Playbook

Goal: make costs explainable: **where** did tokens go, and **who** spent them.

## 1) Log budget events
Write JSONL lines into `.claude-performance/events/<run_id>.jsonl`.

One line per agent step is enough:
- role (Explore/Write/Critic/DecideGap/TeamLead/Judge)
- model
- task (human label)
- prompt_tokens / completion_tokens / total_tokens

## 2) Budget report (deterministic)
Run `budget_analyze` to aggregate and export charts.

## 3) Panel review (LLM-driven, external)
Generate a JSON file: `.claude-performance/reviews/<run_id>_panels.json` with:
- worker_oodle (effort/effectiveness + notes)
- worker_deepseek (effort/effectiveness + notes)
- teamlead (expected effort + self compare)
- judge_oodle (quality + could_be_better + how)

## 4) Consolidate review (deterministic)
Run `efficiency_review` to merge panel + budget into one report and export charts.

## 5) Use the result
- identify top cost driver role/model/task
- decide if you should change routing (cheaper model), reduce context, or improve instructions


## Default behavior
- Enabled by default via `.claude/config/performance_budgeting.yaml`.
- Disable/enable via `performance_toggle` (TeamLead may disable when too expensive).
- End-of-run: call `performance_finalize` to export reports + charts.


## Auto-Logger Hook
After each agent step, call one of:
- `python .claude/tools/token_event_autologger.py` (env-driven)
- Skill `token_event_log` (JSON-driven)

This produces one JSONL line per step for accurate attribution.


## Unified agent step wrapper
Use `.claude/tools/run_agent_step.py` to run each agent step and log one event automatically.


## Publishing
Budget and review reports are also copied into `.report/performance/<run_id>/` for easy discovery.
