#!/usr/bin/env python3
"""
bandit_router_select — Clockwork skill wrapper for BanditRouter (CCW-MVP18).

Calls BanditRouter.select() and returns a SkillResultSpec.  The bandit reads
the outcome ledger to bias model selection, falling back to static YAML routing
or hardcoded defaults when the ledger is too small.

Usage (standalone):
    python bandit_router_select.py '{"skill_id":"bandit_router_select","inputs":{"task_type":"code_review"}}'
    echo '{"skill_id":"bandit_router_select","inputs":{"task_type":"qa_campaign","epsilon":0.2}}' | python bandit_router_select.py

Usage (via skill_runner):
    Dispatched automatically when skill_id == "bandit_router_select".
    Required input: task_type (str).
    Optional inputs: quality_threshold (float), cost_cap (float), epsilon (float), ladder_name (str).

Output (stdout JSON):
    skill_result_spec with status "ok" or "fail".
    outputs.decision contains: model_id, rung, confidence, source.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path bootstrap — importable from .claude/tools/skills/ regardless of cwd
# ---------------------------------------------------------------------------

_SKILL_DIR = Path(__file__).resolve().parent          # .claude/tools/skills/
_PROJECT_ROOT = _SKILL_DIR.parents[2]                  # repo root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec dict.

    Returns a skill_result_spec dict.
    """
    inputs = req.get("inputs", {}) or {}
    request_id = req.get("request_id", "")

    task_type = str(inputs.get("task_type", ""))
    if not task_type:
        return {
            "type": "skill_result_spec",
            "skill_id": "bandit_router_select",
            "request_id": request_id,
            "status": "fail",
            "outputs": {},
            "errors": ["inputs.task_type is required"],
            "warnings": [],
            "metrics": {},
        }

    quality_threshold = float(inputs.get("quality_threshold", 0.7))
    cost_cap = float(inputs.get("cost_cap", 0.05))
    epsilon = float(inputs.get("epsilon", 0.1))
    ladder_name = str(inputs.get("ladder_name", "sonnet"))

    try:
        from llamacode.core.bandit_router import BanditRouter  # type: ignore
    except ImportError as exc:
        return {
            "type": "skill_result_spec",
            "skill_id": "bandit_router_select",
            "request_id": request_id,
            "status": "fail",
            "outputs": {},
            "errors": [
                f"Could not import BanditRouter: {exc}. "
                "Ensure llamacode is on the Python path."
            ],
            "warnings": [],
            "metrics": {},
        }

    try:
        router = BanditRouter(ladder_name=ladder_name, epsilon=epsilon)
        decision = router.select(
            task_type=task_type,
            quality_threshold=quality_threshold,
            cost_cap=cost_cap,
        )
    except Exception as exc:
        return {
            "type": "skill_result_spec",
            "skill_id": "bandit_router_select",
            "request_id": request_id,
            "status": "fail",
            "outputs": {},
            "errors": [f"BanditRouter.select() raised: {exc}"],
            "warnings": [],
            "metrics": {},
        }

    return {
        "type": "skill_result_spec",
        "skill_id": "bandit_router_select",
        "request_id": request_id,
        "status": "ok",
        "outputs": {
            "decision": decision,
        },
        "errors": [],
        "warnings": [],
        "metrics": {
            "selected_model": decision.get("model_id", ""),
            "source": decision.get("source", ""),
            "rung": decision.get("rung", 0),
            "confidence": decision.get("confidence", 0.0),
        },
    }


# ---------------------------------------------------------------------------
# Standalone entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) >= 2:
        raw = sys.argv[1]
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON input: {exc}\n")
        return 1

    if "skill_id" in data or data.get("type") == "skill_request_spec":
        result = run(data)
    else:
        result = run({"skill_id": "bandit_router_select", "inputs": data})

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
