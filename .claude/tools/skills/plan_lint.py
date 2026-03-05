#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def _load_max_plan_tasks() -> int:
    settings = Path(".claude/settings.local.json")
    default_max = 12
    if not settings.exists():
        return default_max
    cfg = _load_json(settings)
    planning = cfg.get("planning", {})
    val = planning.get("max_plan_tasks", planning.get("max_plan_tasks_default", default_max))
    try:
        val = int(val)
    except Exception:
        return default_max
    return max(8, min(12, val))

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    plan_path = Path(inputs.get("plan", "")).resolve()
    schema_path = Path(inputs.get("schema", ".claude/contracts/schemas/plan_spec.schema.json")).resolve()
    max_tasks = _load_max_plan_tasks()

    failures=[]
    if not plan_path.exists():
        failures.append(f"Plan file not found: {plan_path}")
    else:
        plan = _load_json(plan_path)
        tasks = plan.get("tasks", [])
        if isinstance(tasks, list) and len(tasks) > max_tasks:
            failures.append(f"Plan has {len(tasks)} tasks, exceeds max_plan_tasks={max_tasks}")

        # basic structural checks without pulling in heavy deps
        if plan.get("type") != "plan_spec":
            failures.append("Plan type must be 'plan_spec'")
        if not plan.get("goal"):
            failures.append("Plan goal is required")
        acc = plan.get("acceptance", [])
        if not isinstance(acc, list) or len(acc) < 1:
            failures.append("Plan must include acceptance criteria")

    status = "ok" if not failures else "fail"
    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id": req.get("skill_id","plan_lint"),
        "status": status,
        "outputs": {
            "max_plan_tasks": max_tasks,
            "failures": failures
        },
        "metrics": {"failure_count": len(failures)},
        "errors": failures if status=="fail" else [],
        "warnings": []
    }
