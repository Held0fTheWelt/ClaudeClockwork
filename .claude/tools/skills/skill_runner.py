#!/usr/bin/env python3
"""
Skill Runner (tool-first)

Reads a SkillRequestSpec (JSON) from --in file or stdin, dispatches to skill implementations,
and writes a SkillResultSpec to stdout (and optionally --out).

Exit codes:
0 = ok
1 = fail
2 = invalid input spec
"""

from __future__ import annotations
import argparse, json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from repo_validate import run as repo_validate
from evidence_init import run as evidence_init
from spec_validate import run as spec_validate
from determinism_proof import run as determinism_proof
from economics_regression import run as economics_regression
from plan_lint import run as plan_lint
from creativity_burst import run as creativity_burst
from plan_mutate import run as plan_mutate
from hypothesis_builder import run as hypothesis_builder
from prompt_debt_capture import run as prompt_debt_capture
from route_profile_update import run as route_profile_update
from edge_case_selector import run as edge_case_selector
from idea_scoring import run as idea_scoring
from plan_diff_apply import run as plan_diff_apply
from decision_feedback import run as decision_feedback
from deliberation_pack_build import run as deliberation_pack_build
from triad_build import run as triad_build
from triad_ref_lint import run as triad_ref_lint
from outcome_ledger_append import run as outcome_ledger_append
from route_autotune_suggest import run as route_autotune_suggest
from contract_drift_sentinel import run as contract_drift_sentinel
from policy_gatekeeper import run as policy_gatekeeper
from evidence_router import run as evidence_router
from exec_dryrun import run as exec_dryrun
from route_profile_patch_pack import run as route_profile_patch_pack
from outcome_event_generate import run as outcome_event_generate

from doc_ssot_resolver import run as doc_ssot_resolver
from team_topology_verify import run as team_topology_verify
from capability_map_build import run as capability_map_build
from budget_router import run as budget_router
from security_redactor import run as security_redactor
from evidence_bundle_build import run as evidence_bundle_build
from determinism_harness import run as determinism_harness
from refactor_bridge_scan import run as refactor_bridge_scan
from drift_semantic_check import run as drift_semantic_check
from qa_gate import run as qa_gate
from release_cut import run as release_cut
from schema_batch_validate import run as schema_batch_validate

from doc_write import run as doc_write
from tutorial_write import run as tutorial_write
from doc_review import run as doc_review
from repo_compare import run as repo_compare
from screencast_script import run as screencast_script
from pattern_detect import run as pattern_detect
from mutation_detect import run as mutation_detect
from system_map import run as system_map
from mechanic_explain import run as mechanic_explain
from code_assimilate import run as code_assimilate
from log_standardize import run as log_standardize
from copyright_standardize import run as copyright_standardize
from reference_fix import run as reference_fix
from skill_registry_search import run as skill_registry_search
from skill_gap_detect import run as skill_gap_detect
from skill_scaffold import run as skill_scaffold
from repo_clean_scan import run as repo_clean_scan
from code_clean_scan import run as code_clean_scan
from cleanup_plan_apply import run as cleanup_plan_apply
from last_train_merge import run as last_train_merge
from shadow_prompt_minify import run as shadow_prompt_minify
from autodocs_generate import run as autodocs_generate
from hardening_scan_fix import run as hardening_scan_fix
from limitation_harvest_scan import run as limitation_harvest_scan
from pdf_render import run as pdf_render
from pdf_export import run as pdf_export

# MVP02/09/11/20/21 reference skills
from hello import run as hello
from scan import run as scan
from report import run as report
from escalation_router import run as escalation_router
from eval_run import run as eval_run
from create_mvp import run as create_mvp
from clockwork_version_bump import run as clockwork_version_bump

# MVP12 telemetry skills
from telemetry_summarize import run as telemetry_summarize
from review_panel import run as review_panel

# MVP13 cleaning skills
from cleanup_apply import run as cleanup_apply
from repo_clean import run as repo_clean
from code_clean import run as code_clean

# MVP14 archive skills
from last_train import run as last_train
from shadow_prompt import run as shadow_prompt

# MVP15 PDF quality skill
from pdf_quality import run as pdf_quality

# MVP16 parity/registry skills
from parity_scan_and_mvp_planner import run as parity_scan_and_mvp_planner
from idea_dedupe import run as idea_dedupe

# MVP18 adaptive routing skill
from bandit_router_select import run as bandit_router_select


def _ensure_repo_root() -> None:
    """
    Ensure we run from the repository root (where `.claude/` is visible),
    to avoid false-green checks when launched from subdirectories.
    """
    import os
    from pathlib import Path

    cwd = Path.cwd()
    if (cwd / ".claude").exists():
        return
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".claude").exists():
            os.chdir(parent)
            return
    raise RuntimeError("Repository root not found: `.claude/` not visible in current or parent directories.")

from budget_analyze import run as budget_analyze
from efficiency_review import run as efficiency_review
from performance_toggle import run as performance_toggle
from performance_finalize import run as performance_finalize
from critics_board_review import run as critics_board_review
from token_event_log import run as token_event_log
from work_scope_assess import run as work_scope_assess
from model_routing_select import run as model_routing_select
from model_routing_record_outcome import run as model_routing_record_outcome

SKILLS = {
    "triad_build": triad_build,
    "triad_ref_lint": triad_ref_lint,
    "repo_validate": repo_validate,
    "evidence_init": evidence_init,
    "spec_validate": spec_validate,
    "determinism_proof": determinism_proof,
    "economics_regression": economics_regression,
    "plan_lint": plan_lint,
    "creativity_burst": creativity_burst,
    "plan_mutate": plan_mutate,
    "hypothesis_builder": hypothesis_builder,
    "prompt_debt_capture": prompt_debt_capture,
    "route_profile_update": route_profile_update,
    "edge_case_selector": edge_case_selector,
    "idea_scoring": idea_scoring,
    "plan_diff_apply": plan_diff_apply,
    "decision_feedback": decision_feedback,
    "deliberation_pack_build": deliberation_pack_build,
    "outcome_ledger_append": outcome_ledger_append,
    "route_autotune_suggest": route_autotune_suggest,
    "contract_drift_sentinel": contract_drift_sentinel,
    "policy_gatekeeper": policy_gatekeeper,
    "evidence_router": evidence_router,
    "exec_dryrun": exec_dryrun,
    "route_profile_patch_pack": route_profile_patch_pack,
    "outcome_event_generate": outcome_event_generate,
    "doc_ssot_resolver": doc_ssot_resolver,
    "team_topology_verify": team_topology_verify,
    "capability_map_build": capability_map_build,
    "budget_router": budget_router,
    "security_redactor": security_redactor,
    "evidence_bundle_build": evidence_bundle_build,
    "determinism_harness": determinism_harness,
    "refactor_bridge_scan": refactor_bridge_scan,
    "drift_semantic_check": drift_semantic_check,
    "qa_gate": qa_gate,
    "release_cut": release_cut,
    "schema_batch_validate": schema_batch_validate,

    # v17.7 docs addons
    "doc_write": doc_write,
    "tutorial_write": tutorial_write,
    "doc_review": doc_review,
    "repo_compare": repo_compare,
    "screencast_script": screencast_script,
    "pattern_detect": pattern_detect,
    "mutation_detect": mutation_detect,
    "system_map": system_map,
    "mechanic_explain": mechanic_explain,
    "code_assimilate": code_assimilate,
    "log_standardize": log_standardize,
    "copyright_standardize": copyright_standardize,
    "reference_fix": reference_fix,
    "skill_registry_search": skill_registry_search,
    "skill_gap_detect": skill_gap_detect,
    "skill_scaffold": skill_scaffold,
    "repo_clean_scan": repo_clean_scan,
    "cleanup_plan_apply": cleanup_plan_apply,
    "code_clean_scan": code_clean_scan,
    "last_train_merge": last_train_merge,
    "shadow_prompt_minify": shadow_prompt_minify,
    "autodocs_generate": autodocs_generate,
    "hardening_scan_fix": hardening_scan_fix,
    "model_routing_record_outcome": model_routing_record_outcome,
    "model_routing_select": model_routing_select,
    "work_scope_assess": work_scope_assess,
    "critics_board_review": critics_board_review,
    "performance_finalize": performance_finalize,
    "token_event_log": token_event_log,
    "performance_toggle": performance_toggle,
    "budget_analyze": budget_analyze,
    "efficiency_review": efficiency_review,
    "limitation_harvest_scan": limitation_harvest_scan,
    "pdf_render": pdf_render,
    "pdf_export": pdf_export,

    # MVP02/09/11/20/21 reference skills
    "hello": hello,
    "scan": scan,
    "report": report,
    "escalation_router": escalation_router,
    "eval_run": eval_run,
    "create_mvp": create_mvp,
    "clockwork_version_bump": clockwork_version_bump,

    # MVP12 telemetry skills
    "telemetry_summarize": telemetry_summarize,
    "review_panel": review_panel,

    # MVP13 cleaning skills
    "cleanup_apply": cleanup_apply,
    "repo_clean": repo_clean,
    "code_clean": code_clean,

    # MVP14 archive skills
    "last_train": last_train,
    "shadow_prompt": shadow_prompt,

    # MVP15 PDF quality skill
    "pdf_quality": pdf_quality,

    # MVP16 parity/registry skills
    "parity_scan_and_mvp_planner": parity_scan_and_mvp_planner,
    "idea_dedupe": idea_dedupe,

    # MVP18 adaptive routing
    "bandit_router_select": bandit_router_select,
}

def load_json(path: Path | None) -> dict:
    if path:
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(sys.stdin.read())

def dump_json(obj: dict, path: Path | None) -> None:
    s = json.dumps(obj, indent=2, ensure_ascii=False)
    if path:
        path.write_text(s, encoding="utf-8")
    else:
        sys.stdout.write(s + "\n")


# --- Auto logging for deterministic skills (budget events) ---
def _autolog_skill_event(skill_id: str, status: str, metrics: dict) -> None:
    try:
        cfg_path = Path(".claude/config/performance_budgeting.yaml").resolve()
        if not cfg_path.exists():
            return
        cfg = json.loads(cfg_path.read_text(encoding="utf-8", errors="ignore"))
        if not bool(cfg.get("enabled", True)):
            return
        # Only log deterministic skill executions (tokens=0). Real LLM actions should use token_event_autologger or token_event_log.
        run_id = os.getenv("CLOCKWORK_RUN_ID", "run-unknown")
        role = os.getenv("CLOCKWORK_ROLE", "Tool")
        model = os.getenv("CLOCKWORK_MODEL", "deterministic")
        task = os.getenv("CLOCKWORK_TASK", skill_id)
        event = {
            "ts": now_iso(),
            "run_id": run_id,
            "role": role,
            "model": model,
            "task": task,
            "phase": "skill",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "notes": f"skill_id={skill_id} status={status} metrics={metrics}"
        }
        events_file = resolve_events_file(run_id, None)
        append_event(event, events_file)
    except Exception:
        return

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", default=None)
    ap.add_argument("--out", dest="outfile", default=None)
    args = ap.parse_args()

    req = None
    try:
        req = load_json(Path(args.infile) if args.infile else None)
    except Exception as e:
        sys.stderr.write(f"Invalid JSON input: {e}\n")
        return 2

    if not isinstance(req, dict) or req.get("type") != "skill_request_spec":
        sys.stderr.write("Invalid request: expected type=skill_request_spec\n")
        return 2

    # Ensure consistent CWD: run from repo root where `.claude/` is visible
    try:
        _ensure_repo_root()
    except Exception as e:
        res = {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", ""),
            "status": "fail",
            "outputs": {},
            "errors": [f"Repo root not found: {e}"],
            "warnings": [],
            "metrics": {},
        }
        dump_json(res, Path(args.outfile) if args.outfile else None)
        return 1

    # Optional input validation (opt-in via validate_input=True in the request).
    # When enabled, spec_validate is called on the inputs before dispatching.
    # This is non-breaking: the flag defaults to absent/False; existing requests
    # are unaffected and no schema file is required.
    if req.get("validate_input") is True:
        try:
            val_result = spec_validate(req)
            if val_result.get("status") != "ok":
                val_errors = val_result.get("errors", [])
                res = {
                    "type": "skill_result_spec",
                    "request_id": req.get("request_id", ""),
                    "skill_id": req.get("skill_id", ""),
                    "status": "fail",
                    "outputs": {},
                    "errors": ["validate_input failed"] + val_errors,
                    "warnings": [],
                    "metrics": {},
                }
                dump_json(res, Path(args.outfile) if args.outfile else None)
                return 1
        except Exception as e:
            # spec_validate errors must not crash the runner; emit a warning and continue
            sys.stderr.write(f"[skill_runner] validate_input raised: {e}\n")

    skill_id = req.get("skill_id")
    fn = SKILLS.get(skill_id)
    if not fn:
        try:
            from claudeclockwork.bridge import run_manifest_skill
            bridged = run_manifest_skill(req, REPO_ROOT)
        except Exception as exc:
            bridged = {
                "type": "skill_result_spec",
                "request_id": req.get("request_id", ""),
                "skill_id": skill_id or "",
                "status": "fail",
                "outputs": {},
                "errors": [f"Manifest bridge failed: {exc}"],
                "warnings": [],
                "metrics": {},
            }
        if bridged is None:
            res = {
                "type": "skill_result_spec",
                "request_id": req.get("request_id", ""),
                "skill_id": skill_id or "",
                "status": "fail",
                "outputs": {},
                "errors": [f"Unknown skill_id: {skill_id}"],
                "warnings": [],
                "metrics": {},
            }
            dump_json(res, Path(args.outfile) if args.outfile else None)
            return 1
        dump_json(bridged, Path(args.outfile) if args.outfile else None)
        return 0 if bridged.get("status") == "ok" else 1

    res = fn(req)
    dump_json(res, Path(args.outfile) if args.outfile else None)
    return 0 if res.get("status") == "ok" else 1

if __name__ == "__main__":
    raise SystemExit(main())
