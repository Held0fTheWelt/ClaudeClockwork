# Cleaning Playbook (Docs + Code)

Goal: clean up stale files **without losing knowledge**.

## 0) Rules of engagement
1) Prefer **archive** over delete.
2) Every cleanup produces a **report** and a **plan** (machine-readable).
3) Require a human review for anything below "high" confidence.

## 1) Repo cleanup (docs/files)
Run `repo_clean_scan`:
- Entry docs define what is "reachable"
- Convention roots are always considered in-use

Then:
- execute manual cleanup OR
- feed the plan into a controlled apply-step (future)

## 2) Code cleanup
Run `code_clean_scan`:
- scan `.claude/tools/skills` or your target code roots
- use skill_runner as the entrypoint to compute reachability

Then:
- if orphans are confirmed: move to `.claude/_archive/code/YYYY-MM-DD/`
- update registry + skill_runner mapping if the code is still needed

## 3) Always document limitations
When you generate “First Steps”, “Lastenheft”, “API Reference”, etc. include:
- **Current limitations**
- **Non-goals**
- **Known gaps / TODOs**
- **What users might assume, but is not implemented**


## 4) Apply (optional, controlled)
After review, apply the plan with `cleanup_plan_apply`:
- start with `dry_run=true`
- keep `allow_delete=false` unless absolutely needed
