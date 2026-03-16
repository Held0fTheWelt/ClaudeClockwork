#!/usr/bin/env python3
from __future__ import annotations
import json

REQUIRED_BRIEF_FIELDS = ["goal", "tasks", "acceptance"]  # constraints optional

def _word_count(s: str) -> int:
    return len([w for w in s.strip().split() if w])

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    triad = inputs.get("triad")
    if not isinstance(triad, dict) or triad.get("type") != "message_triad_spec":
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"triad_ref_lint","status":"fail","outputs":{},
                "metrics":{}, "errors":["inputs.triad must be a MessageTriadSpec object"], "warnings":[]}

    problems=[]
    wb = triad.get("work_brief", {}) or {}
    brief = wb.get("brief", {}) or {}
    budget = wb.get("budget", {}) or {}

    # Required fields
    for f in REQUIRED_BRIEF_FIELDS:
        val = brief.get(f)
        if val is None or (isinstance(val, str) and not val.strip()) or (isinstance(val, list) and len(val) == 0):
            problems.append(f"work_brief.brief.{f} is missing/empty")

    # tasks cap (8–12) if provided via inputs
    max_plan_tasks = inputs.get("max_plan_tasks")
    try:
        max_plan_tasks = int(max_plan_tasks) if max_plan_tasks is not None else None
    except Exception:
        max_plan_tasks = None
    tasks = brief.get("tasks", []) if isinstance(brief.get("tasks", []), list) else []
    if max_plan_tasks is not None and len(tasks) > max_plan_tasks:
        problems.append(f"tasks length {len(tasks)} exceeds max_plan_tasks={max_plan_tasks}")

    # word/char budgets (approx; only on the concatenated brief fields)
    text_blob = " ".join([
        str(brief.get("goal","")),
        " ".join(brief.get("context",[]) if isinstance(brief.get("context",[]), list) else []),
        " ".join(brief.get("constraints",[]) if isinstance(brief.get("constraints",[]), list) else []),
        " ".join(tasks),
        " ".join(brief.get("acceptance",[]) if isinstance(brief.get("acceptance",[]), list) else []),
    ]).strip()

    max_words = budget.get("max_words")
    max_chars = budget.get("max_chars")

    try:
        if max_words is not None and _word_count(text_blob) > int(max_words):
            problems.append(f"work_brief exceeds max_words={max_words}")
    except Exception:
        pass

    try:
        if max_chars is not None and len(text_blob) > int(max_chars):
            problems.append(f"work_brief exceeds max_chars={max_chars}")
    except Exception:
        pass

    status = "ok" if not problems else "fail"
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"triad_ref_lint","status": status,
            "outputs":{"problems": problems, "word_count": _word_count(text_blob), "char_count": len(text_blob)},
            "metrics":{"problem_count": len(problems)}, "errors": (problems if status=="fail" else []),
            "warnings":[]}
