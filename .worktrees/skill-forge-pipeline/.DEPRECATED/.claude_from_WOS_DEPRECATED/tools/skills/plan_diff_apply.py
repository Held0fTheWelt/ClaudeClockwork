#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    plan_path = Path(inputs.get("plan","")).resolve()
    diff_path = Path(inputs.get("diff","")).resolve()
    if not plan_path.exists() or not diff_path.exists():
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"plan_diff_apply","status":"fail","outputs":{},
                "metrics":{}, "errors":["plan or diff file not found"], "warnings":[]}

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    diff = json.loads(diff_path.read_text(encoding="utf-8"))
    changes = diff.get("changes", {})
    add = set(changes.get("add_tasks", []))
    rem = set(changes.get("remove_tasks", []))

    tasks = plan.get("tasks", [])
    if not isinstance(tasks, list):
        tasks = []
    # remove by id
    tasks = [t for t in tasks if not (isinstance(t, dict) and t.get("id") in rem)]
    # add placeholders
    for tid in add:
        tasks.append({"id": tid, "title": f"ADDED:{tid}", "steps": ["Define steps"]})
    plan["tasks"] = tasks
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"plan_diff_apply","status":"ok",
            "outputs":{"updated_plan": plan, "task_count": len(tasks)},
            "metrics":{"task_count": len(tasks)}, "errors":[], "warnings":[]}
