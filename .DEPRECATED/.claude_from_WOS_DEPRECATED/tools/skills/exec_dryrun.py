#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    cmd = inputs.get("command_spec")
    if not isinstance(cmd, dict) or cmd.get("type") != "command_spec":
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"exec_dryrun","status":"fail","outputs":{},
                "metrics":{}, "errors":["inputs.command_spec must be a CommandSpec"], "warnings":[]}

    cwd = Path(cmd.get("cwd","."))
    exists = cwd.exists() and cwd.is_dir()

    # Very conservative checks only (dry run)
    problems=[]
    if not exists:
        problems.append(f"cwd does not exist: {cwd}")
    if not isinstance(cmd.get("expected_exit_codes"), list) or not cmd.get("expected_exit_codes"):
        problems.append("expected_exit_codes must be a non-empty list")
    if not isinstance(cmd.get("timeout_seconds"), int) or cmd.get("timeout_seconds") <= 0:
        problems.append("timeout_seconds must be positive int")

    status = "ok" if not problems else "fail"
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"exec_dryrun","status": status,
            "outputs":{"problems": problems, "command_id": cmd.get("id","")},
            "metrics":{"problem_count": len(problems)}, "errors": (problems if status=="fail" else []),
            "warnings":[]}
