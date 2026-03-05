# Model Routing (Personaler) Playbook

Goal: always choose the **cheapest model that is likely good enough**, while learning from outcomes.

## Roles
- **Personaler**: selects model based on scope + historical hit list
- **Routing Critic**: checks whether the selection criteria are sound
- **Personaler Response**: defends or proposes alternative parameters
- **Routing Critic Reply**: responds to the defense
- **Personaler Decision**: writes final policy note + updates brain

## Deterministic skills (core automation)
1) `work_scope_assess` → `.report/routing/<run_id>/work_scope_report.json`
2) `model_routing_select` → model selection report + alternatives
3) After execution: `model_routing_record_outcome` updates `.llama_runtime/brain/model_routing_stats.json`

## Inputs the Personaler should consider
- scope tier (low/medium/high)
- risk flags (security/legal)
- ambiguity (need stronger model)
- history: success rate per model per task_type
- cost estimate ranges

## Critic checklist (suggested)
- Are the scope signals adequate? (files_touched, ambiguity, risk)
- Should thresholds be adjusted?
- Does success tracking use meaningful definitions?
- Are we overfitting to small sample sizes?
- Are we missing a cheaper model that would pass?

## Storage
- Decisions + reports: `.report/routing/<run_id>/`
- Long-term stats: `.llama_runtime/brain/model_routing_stats.json`
