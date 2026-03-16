#!/usr/bin/env python3
"""
escalation_router — Clockwork skill wrapper for EscalationRouter.

Routes messages through the cheapest model first and escalates automatically
on overload, timeout, or empty response.

Usage (standalone):
    python escalation_router.py '{"skill_id":"escalation_router","inputs":{"ladder":"haiku","messages":[{"role":"user","content":"hello"}],"dry_run":true}}'
    echo '{"skill_id":"escalation_router","inputs":{"ladder":"haiku","messages":[{"role":"user","content":"hi"}],"dry_run":true}}' | python escalation_router.py

Usage (via skill_runner):
    The run(req) interface is called with a SkillRequestSpec dict.
    req["inputs"]["ladder"] must be "haiku" or "sonnet".
    req["inputs"]["messages"] must be a non-empty list of role/content dicts.

Output (stdout JSON):
    skill_result_spec with status "ok", "all_rungs_exhausted", or "error"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path bootstrap — allow import from project root regardless of cwd
# ---------------------------------------------------------------------------

_SKILL_DIR = Path(__file__).resolve().parent          # .claude/tools/skills/
_PROJECT_ROOT = _SKILL_DIR.parents[2]                  # repo root: .claude/tools/skills -> .claude/tools -> .claude -> repo root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_CONFIG_PATH = _PROJECT_ROOT / ".claude" / "config" / "model_escalation_ladder.yaml"


# ---------------------------------------------------------------------------
# Config loader (mirrors the helper in escalation_router core but self-contained)
# ---------------------------------------------------------------------------

def _load_ladder_config(ladder: str) -> dict:
    """Load the full YAML config and return the config dict for the given ladder.

    Returns the raw ladders[ladder] dict on success, or raises on failure.
    """
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Escalation ladder config not found: {_CONFIG_PATH}"
        )

    raw = _CONFIG_PATH.read_text(encoding="utf-8")

    try:
        import yaml  # type: ignore
        cfg = yaml.safe_load(raw)
    except ImportError:
        raise ImportError(
            "PyYAML is required for dry_run config loading. "
            "Install with: pip install pyyaml"
        )

    ladders = cfg.get("ladders", {})
    if ladder not in ladders:
        available = list(ladders.keys())
        raise ValueError(
            f"Ladder '{ladder}' not found in config. Available: {available}"
        )

    return ladders[ladder]


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec dict.

    Returns a skill_result_spec dict.
    """
    inputs = req.get("inputs", {})
    ladder = str(inputs.get("ladder", "haiku"))
    messages = list(inputs.get("messages", []))
    max_tokens = int(inputs.get("max_tokens", 1024))
    dry_run = bool(inputs.get("dry_run", False))

    request_id = req.get("request_id", "")
    warnings: list[str] = []
    errors: list[str] = []

    # ------------------------------------------------------------------
    # dry_run path — return ladder config without calling any API
    # ------------------------------------------------------------------
    if dry_run:
        try:
            ladder_config = _load_ladder_config(ladder)
        except FileNotFoundError as exc:
            return {
                "type": "skill_result_spec",
                "skill_id": "escalation_router",
                "request_id": request_id,
                "status": "error",
                "outputs": {},
                "errors": [str(exc)],
                "warnings": [],
                "metrics": {},
            }
        except ImportError as exc:
            return {
                "type": "skill_result_spec",
                "skill_id": "escalation_router",
                "request_id": request_id,
                "status": "error",
                "outputs": {},
                "errors": [str(exc)],
                "warnings": [],
                "metrics": {},
            }
        except ValueError as exc:
            return {
                "type": "skill_result_spec",
                "skill_id": "escalation_router",
                "request_id": request_id,
                "status": "error",
                "outputs": {},
                "errors": [str(exc)],
                "warnings": [],
                "metrics": {},
            }

        return {
            "type": "skill_result_spec",
            "skill_id": "escalation_router",
            "request_id": request_id,
            "status": "ok",
            "outputs": {
                "model_used": None,
                "rung": None,
                "content": None,
                "escalated": False,
                "escalation_reason": None,
                "ladder_config": ladder_config,
            },
            "errors": [],
            "warnings": ["dry_run=True: no API call made"],
            "metrics": {},
        }

    # ------------------------------------------------------------------
    # live path — import core and call the API
    # ------------------------------------------------------------------
    try:
        from claudeclockwork.core.escalation_router import (  # type: ignore
            EscalationRouter,
            AllRungsExhausted,
        )
    except ImportError as exc:
        return {
            "type": "skill_result_spec",
            "skill_id": "escalation_router",
            "request_id": request_id,
            "status": "error",
            "outputs": {},
            "errors": [
                f"Could not import EscalationRouter: {exc}. "
                "EscalationRouter has not yet been migrated to claudeclockwork. "
                "This skill is planned for Phase 3 (Native Core Services)."
            ],
            "warnings": warnings,
            "metrics": {},
        }

    try:
        router = EscalationRouter(ladder)
        result = router.call(messages, max_tokens=max_tokens)
        return {
            "type": "skill_result_spec",
            "skill_id": "escalation_router",
            "request_id": request_id,
            "status": "ok",
            "outputs": {
                "model_used": result["model_used"],
                "rung": result["rung"],
                "content": result["content"],
                "escalated": result["escalated"],
                "escalation_reason": result.get("escalation_reason"),
            },
            "errors": [],
            "warnings": warnings,
            "metrics": {
                "rung_used": result["rung"],
                "escalated": int(result["escalated"]),
            },
        }

    except AllRungsExhausted as exc:
        return {
            "type": "skill_result_spec",
            "skill_id": "escalation_router",
            "request_id": request_id,
            "status": "all_rungs_exhausted",
            "outputs": {},
            "errors": [str(exc)],
            "warnings": warnings,
            "metrics": {},
        }

    except Exception as exc:
        return {
            "type": "skill_result_spec",
            "skill_id": "escalation_router",
            "request_id": request_id,
            "status": "error",
            "outputs": {},
            "errors": [str(exc)],
            "warnings": warnings,
            "metrics": {},
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

    # Accept a full SkillRequestSpec (has skill_id at top level)
    # or a bare inputs dict for quick CLI use
    if "skill_id" in data or data.get("type") == "skill_request_spec":
        result = run(data)
    else:
        # Bare inputs dict — wrap it
        result = run({"skill_id": "escalation_router", "inputs": data})

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    ok = result.get("status") == "ok"
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
