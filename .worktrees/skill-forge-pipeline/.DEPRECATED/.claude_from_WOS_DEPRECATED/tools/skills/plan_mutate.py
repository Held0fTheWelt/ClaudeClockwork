#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

PRESETS = {
  "cost_first": {"max_tasks": 8, "notes": "Prefer tool-first validation, keep plan tiny."},
  "reliability_first": {"max_tasks": 12, "notes": "Add verification steps and evidence requirements."},
  "speed_first": {"max_tasks": 8, "notes": "Minimize steps, defer non-critical checks."}
}

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    plan_path = Path(inputs.get("plan","")).resolve()
    preset = inputs.get("preset","cost_first")
    if preset not in PRESETS:
        preset = "cost_first"

    if not plan_path.exists():
        return {
            "type":"skill_result_spec",
            "request_id": req.get("request_id",""),
            "skill_id": req.get("skill_id","plan_mutate"),
            "status":"fail",
            "outputs": {},
            "metrics": {},
            "errors": [f"Plan file not found: {plan_path}"],
            "warnings": []
        }

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    tasks = plan.get("tasks", [])
    if not isinstance(tasks, list):
        tasks = []

    max_tasks = PRESETS[preset]["max_tasks"]
    mutated = dict(plan)
    mutated["notes"] = (mutated.get("notes","") + f" | preset={preset}: {PRESETS[preset]['notes']}").strip()

    # simple mutation: truncate or keep tasks; add evidence_required for reliability_first
    if len(tasks) > max_tasks:
        mutated["tasks"] = tasks[:max_tasks]
    else:
        mutated["tasks"] = tasks

    if preset == "reliability_first":
        for t in mutated["tasks"]:
            if isinstance(t, dict):
                er = t.get("evidence_required", [])
                if "reports/" not in "".join(er):
                    er = list(er) + ["reports/ (proof)"]
                t["evidence_required"] = er

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id": req.get("skill_id","plan_mutate"),
        "status":"ok",
        "outputs":{
            "preset": preset,
            "max_tasks": max_tasks,
            "mutated_plan": mutated
        },
        "metrics":{"task_count": len(mutated.get("tasks",[]))},
        "errors":[],
        "warnings":[]
    }
