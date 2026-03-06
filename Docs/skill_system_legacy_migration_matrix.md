# Skill System Legacy Migration Matrix
Diese Matrix ordnet alle aktuellen Python-Skill-Module aus `.claude/tools/skills/` in die Migrationsstrategie des manifest-basierten Full Skill Systems ein.
## Kurzfazit
- Legacy-Python-Module geprüft: **94**
- Bereits manifest-wrapped: **28**
- Weiter vorerst als Legacy behalten: **60**
- Nur intern: **2**
- Kompatibilitätsbrücke: **1**
- Später stilllegen: **3**

## Legende
- `wrap_now`: bereits ins neue System eingebunden
- `keep_legacy`: vorerst behalten, später wrappen oder nativ neu schreiben
- `repurpose_bridge`: nur noch als Kompatibilitäts- oder Übergangsschicht behalten
- `internal_only`: keine öffentliche Skill-Oberfläche
- `retire_later`: Demo-/Referenzbestand, später entfernen

## Matrix
| Skill | Kategorie | Aktion | Priorität | Beschreibung | Notiz |
|---|---|---|---|---|---|
| _event_logger | internal | internal_only | P3 | !/usr/bin/env python3 | Keep internal helper only; integrate later via runtime events/artifact publishing. |
| _report_publish | internal | internal_only | P3 | !/usr/bin/env python3 | Keep internal helper only; integrate later via runtime events/artifact publishing. |
| autodocs_generate | docs | keep_legacy | P2 | !/usr/bin/env python3 | Keep until document service and artifact layer are formalized. |
| bandit_router_select | routing | keep_legacy | P2 | !/usr/bin/env python3 | Useful routing/adaptation logic; migrate after planner/runtime hooks exist. |
| budget_analyze | performance | keep_legacy | P2 | !/usr/bin/env python3 | Keep until telemetry/runtime config service exists. |
| budget_router | routing | keep_legacy | P2 | !/usr/bin/env python3 | Useful routing/adaptation logic; migrate after planner/runtime hooks exist. |
| capability_map_build | meta | wrap_now | P0 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| cleanup_apply | cleanup | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| cleanup_plan_apply | cleanup | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| clockwork_version_bump | misc | keep_legacy | P2 | !/usr/bin/env python3 | Legacy utility; reassess after core migration wave completes. |
| code_assimilate | analysis | keep_legacy | P2 | !/usr/bin/env python3 | Keep until analysis/artifact contracts are stabilized. |
| code_clean | cleanup | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| code_clean_scan | cleanup | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| contract_drift_sentinel | qa | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| copyright_standardize | docs | keep_legacy | P2 | !/usr/bin/env python3 | Keep until document service and artifact layer are formalized. |
| create_mvp | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| creativity_burst | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| critics_board_review | misc | keep_legacy | P2 | !/usr/bin/env python3 | Legacy utility; reassess after core migration wave completes. |
| decision_feedback | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| deliberation_pack_build | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| determinism_harness | qa | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| determinism_proof | qa | keep_legacy | P1 | !/usr/bin/env python3 | High-value validation capability; migrate after manifest contracts harden. |
| doc_review | docs | keep_legacy | P2 | !/usr/bin/env python3 | Keep until document service and artifact layer are formalized. |
| doc_ssot_resolver | docs | keep_legacy | P2 | !/usr/bin/env python3 | Keep until document service and artifact layer are formalized. |
| doc_write | docs | keep_legacy | P2 | !/usr/bin/env python3 | Keep until document service and artifact layer are formalized. |
| drift_semantic_check | qa | keep_legacy | P1 | !/usr/bin/env python3 | High-value validation capability; migrate after manifest contracts harden. |
| economics_regression | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| edge_case_selector | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| efficiency_review | misc | keep_legacy | P2 | !/usr/bin/env python3 | Legacy utility; reassess after core migration wave completes. |
| escalation_router | routing | keep_legacy | P2 | !/usr/bin/env python3 | Useful routing/adaptation logic; migrate after planner/runtime hooks exist. |
| eval_run | misc | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| evidence_bundle_build | evidence | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| evidence_init | evidence | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| evidence_router | evidence | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| exec_dryrun | misc | keep_legacy | P2 | !/usr/bin/env python3 | Legacy utility; reassess after core migration wave completes. |
| hardening_scan_fix | qa | keep_legacy | P1 | !/usr/bin/env python3 | High-value validation capability; migrate after manifest contracts harden. |
| hello | demo | retire_later | P3 | !/usr/bin/env python3 | Keep only as demo/reference skill; remove once native smoke/demo coverage is enough. |
| hypothesis_builder | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| idea_dedupe | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| idea_scoring | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| last_train | archive | keep_legacy | P2 | !/usr/bin/env python3 | Keep until archive and prompt-ops subsystems exist. |
| last_train_merge | archive | keep_legacy | P2 | !/usr/bin/env python3 | Keep until archive and prompt-ops subsystems exist. |
| limitation_harvest_scan | analysis | keep_legacy | P2 | !/usr/bin/env python3 | Keep until analysis/artifact contracts are stabilized. |
| log_standardize | misc | keep_legacy | P2 | !/usr/bin/env python3 | Legacy utility; reassess after core migration wave completes. |
| mechanic_explain | analysis | keep_legacy | P2 | !/usr/bin/env python3 | Keep until analysis/artifact contracts are stabilized. |
| model_routing_record_outcome | routing | keep_legacy | P2 | !/usr/bin/env python3 | Useful routing/adaptation logic; migrate after planner/runtime hooks exist. |
| model_routing_select | routing | keep_legacy | P2 | !/usr/bin/env python3 | Useful routing/adaptation logic; migrate after planner/runtime hooks exist. |
| mutation_detect | analysis | keep_legacy | P2 | !/usr/bin/env python3 | Keep until analysis/artifact contracts are stabilized. |
| outcome_event_generate | evidence | keep_legacy | P1 | !/usr/bin/env python3 | Preserve for artifact/release pipeline; migrate after bundle contract is richer. |
| outcome_ledger_append | evidence | keep_legacy | P1 | !/usr/bin/env python3 | Preserve for artifact/release pipeline; migrate after bundle contract is richer. |
| parity_scan_and_mvp_planner | planning | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| pattern_detect | analysis | keep_legacy | P2 | !/usr/bin/env python3 | Keep until analysis/artifact contracts are stabilized. |
| pdf_export | docs | keep_legacy | P2 | !/usr/bin/env python3 | Keep until document service and artifact layer are formalized. |
| pdf_quality | docs | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| pdf_render | docs | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| performance_finalize | performance | keep_legacy | P2 | !/usr/bin/env python3 | Keep until telemetry/runtime config service exists. |
| performance_toggle | performance | keep_legacy | P2 | !/usr/bin/env python3 | Keep until telemetry/runtime config service exists. |
| plan_diff_apply | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| plan_lint | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| plan_mutate | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| policy_gatekeeper | qa | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| prompt_debt_capture | misc | keep_legacy | P2 | !/usr/bin/env python3 | Legacy utility; reassess after core migration wave completes. |
| qa_gate | qa | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| refactor_bridge_scan | meta | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| reference_fix | docs | keep_legacy | P2 | !/usr/bin/env python3 | Keep until document service and artifact layer are formalized. |
| release_cut | evidence | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| repo_clean | cleanup | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| repo_clean_scan | cleanup | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| repo_compare | misc | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| repo_validate | qa | wrap_now | P0 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| report | demo | retire_later | P3 | !/usr/bin/env python3 | Keep only as demo/reference skill; remove once native smoke/demo coverage is enough. |
| review_panel | misc | keep_legacy | P2 | !/usr/bin/env python3 | Legacy utility; reassess after core migration wave completes. |
| route_autotune_suggest | routing | keep_legacy | P2 | !/usr/bin/env python3 | Useful routing/adaptation logic; migrate after planner/runtime hooks exist. |
| route_profile_patch_pack | routing | keep_legacy | P2 | !/usr/bin/env python3 | Useful routing/adaptation logic; migrate after planner/runtime hooks exist. |
| route_profile_update | routing | keep_legacy | P2 | !/usr/bin/env python3 | Useful routing/adaptation logic; migrate after planner/runtime hooks exist. |
| scan | demo | retire_later | P3 | !/usr/bin/env python3 | Keep only as demo/reference skill; remove once native smoke/demo coverage is enough. |
| schema_batch_validate | qa | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| screencast_script | docs | keep_legacy | P2 | !/usr/bin/env python3 | Keep until document service and artifact layer are formalized. |
| security_redactor | misc | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| shadow_prompt | archive | keep_legacy | P2 | !/usr/bin/env python3 | Keep until archive and prompt-ops subsystems exist. |
| shadow_prompt_minify | archive | keep_legacy | P2 | !/usr/bin/env python3 | Keep until archive and prompt-ops subsystems exist. |
| skill_gap_detect | meta | wrap_now | P1 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| skill_registry_search | meta | wrap_now | P0 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| skill_runner | runtime | repurpose_bridge | P0 | !/usr/bin/env python3 | Keep as compatibility bridge only; stop adding new hard-coded dispatch logic. |
| skill_scaffold | meta | wrap_now | P0 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| spec_validate | qa | wrap_now | P0 | !/usr/bin/env python3 | Already exposed through the manifest-based runtime. |
| system_map | analysis | keep_legacy | P2 | !/usr/bin/env python3 | Keep until analysis/artifact contracts are stabilized. |
| team_topology_verify | qa | keep_legacy | P1 | !/usr/bin/env python3 | High-value validation capability; migrate after manifest contracts harden. |
| telemetry_summarize | performance | keep_legacy | P2 | !/usr/bin/env python3 | Keep until telemetry/runtime config service exists. |
| token_event_log | performance | keep_legacy | P2 | !/usr/bin/env python3 | Keep until telemetry/runtime config service exists. |
| triad_build | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| triad_ref_lint | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
| tutorial_write | docs | keep_legacy | P2 | !/usr/bin/env python3 | Keep until document service and artifact layer are formalized. |
| work_scope_assess | planning | keep_legacy | P2 | !/usr/bin/env python3 | Keep until planner/executor contract supports multi-step decisions. |
