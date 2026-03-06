# MVP Phase 7 — Wrapper Wave 4 (Legacy CLI Gap)

**Goal:** Eliminate the undocumented dual-dispatch split. Bring the remaining 54 legacy-only skills into the manifest registry so they are reachable via `python3 -m claudeclockwork.cli`.

**Source finding:** VERIFY 2026-03-06 — Risk C2: "63 skills unreachable via CLI. The old `skill_runner.py` path is the only way to reach them. This is an undocumented split."
**Current state (post Phase 2):** 45 manifest skills, 54 legacy-only (no manifest).

---

## Definition of Done

- [ ] All 54 legacy-only skills have a `manifest.json` and `LegacySkillAdapter` wrapper
- [ ] `capability_map_build` reports ≥ 99 manifest skills
- [ ] All 54 new skills are discoverable via `python3 -m claudeclockwork.cli --skill-id <id>`
- [ ] Phase 6 gate baseline updated (`python3 scripts/update_baselines.py`)
- [ ] All existing tests pass

---

## Skills to Wrap (54 total)

### Routing (8)
| Skill | Notes |
|-------|-------|
| `bandit_router_select` | Contains stale `llamacode` import comment — remove before wrapping |
| `budget_router` | Contains `oodle_tier` variable — rename to `local_model_tier` before wrapping |
| `budget_analyze` | Budget analysis |
| `escalation_router` | Contains stale `llamacode` import comment — remove before wrapping |
| `model_routing_select` | Model routing |
| `model_routing_record_outcome` | Routing outcome ledger |
| `route_autotune_suggest` | Routing optimization |
| `route_profile_update` | Routing profile writer |

> Note: `route_profile_patch_pack` is listed in the roadmap but not found in `skill_runner.py` — verify existence before wrapping.

### Planning (15)
| Skill | Notes |
|-------|-------|
| `create_mvp` | |
| `creativity_burst` | |
| `decision_feedback` | |
| `deliberation_pack_build` | |
| `economics_regression` | |
| `edge_case_selector` | |
| `hypothesis_builder` | |
| `idea_dedupe` | |
| `idea_scoring` | |
| `plan_diff_apply` | |
| `plan_lint` | |
| `plan_mutate` | |
| `triad_build` | |
| `triad_ref_lint` | |
| `work_scope_assess` | |

### Analysis (6)
| Skill | Notes |
|-------|-------|
| `code_assimilate` | |
| `limitation_harvest_scan` | |
| `mechanic_explain` | |
| `mutation_detect` | |
| `pattern_detect` | |
| `system_map` | |

### Docs (9)
| Skill | Notes |
|-------|-------|
| `autodocs_generate` | |
| `copyright_standardize` | |
| `doc_review` | |
| `doc_ssot_resolver` | |
| `doc_write` | |
| `pdf_export` | |
| `screencast_script` | |
| `tutorial_write` | |
| `log_standardize` | |

### Performance / Budget (5)
| Skill | Notes |
|-------|-------|
| `token_event_log` | |
| `prompt_debt_capture` | |
| `efficiency_review` | May require matplotlib — check before wrapping |
| `shadow_prompt` | |
| `shadow_prompt_minify` | |

### Archive / Misc (7)
| Skill | Notes |
|-------|-------|
| `last_train` | |
| `last_train_merge` | |
| `critics_board_review` | |
| `exec_dryrun` | |
| `review_panel` | |
| `report` | Demo skill — wrap as `category: demo` |
| `scan` | Demo skill — wrap as `category: demo` |

### Internal helpers (2 — do NOT wrap)
| Skill | Notes |
|-------|-------|
| `_event_logger` | Internal helper — no manifest, no CLI exposure |
| `_report_publish` | Internal helper — no manifest, no CLI exposure |

> `hello` was previously identified as demo/retire — check if still present and wrap as `category: demo` if so.

---

## Deliverables per skill

- `manifest.json` (`id`, `name`, `version: "1.0.0"`, `description`, `category`, `entrypoint`, `permissions`, `metadata: {"legacy_bridge": "<skill_name>"}`)
- `__init__.py`, `skill.py` extending `LegacySkillAdapter`
- Category directories created if new: `routing/`, `planning/`, `analysis/`, `archive/`

## Acceptance criteria

- `capability_map_build` reports ≥ 99 manifest skills
- `python3 -m claudeclockwork.cli --skill-id budget_router --inputs '{}'` returns a result dict (any status)
- All Phase 6 gates pass after baseline update
- `_event_logger` and `_report_publish` remain legacy-internal (no manifests created for them)

---

## Notes

- Fix `bandit_router_select.py` and `escalation_router.py` `llamacode` import stubs **before** wrapping (see Phase 8 hygiene — can be done inline here)
- Fix `budget_router.py` `oodle_tier` variable name **before** wrapping (see Phase 8 hygiene)
- `efficiency_review` imports `matplotlib` — test that `LegacySkillAdapter` catches `ImportError` gracefully; if not, wrap with `try/except` in the adapter
- After this phase, `skill_runner.py` remains operational but becomes a legacy runtime only — all skills are now reachable via both paths

## Files Changed / Created

| Area | Change |
|------|--------|
| `.claude/skills/routing/*/` | 8 new skill packages |
| `.claude/skills/planning/*/` | 15 new skill packages |
| `.claude/skills/analysis/*/` | 6 new skill packages |
| `.claude/skills/docs/*/` | 9 new skill packages (in existing `docs/` dir) |
| `.claude/skills/performance/*/` | 5 new skill packages (in existing `performance/` dir) |
| `.claude/skills/archive/*/` | New category dir + 2 skill packages |
| `.claude/skills/misc/*/` | 5 new skill packages (in existing `misc/` dir) |
| `scripts/update_baselines.py` | Run after wrapping to refresh Phase 6 baseline |
| `tests/test_wrapper_wave4.py` | New — smoke test all 52 wrapped skills via `run_manifest_skill` |
