#!/usr/bin/env python3
from __future__ import annotations

TEMPLATES = {
  "flaky_tests": {
    "evidence_required": ["logs/test_runs.txt", "reports/flaky_summary.md"],
    "notes": "Run tests 3x, track intermittency, isolate test group."
  },
  "big_refactor": {
    "evidence_required": ["artifacts/diff.patch", "reports/refactor_scope.md"],
    "notes": "Freeze behavior, add characterization tests, refactor in small slices."
  },
  "security_privacy": {
    "evidence_required": ["reports/privacy_scan.json", "reports/policy_gate.md"],
    "notes": "Redaction proof, allowlist check, no secret leakage."
  }
}

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    signals = inputs.get("signals", [])
    if isinstance(signals, str):
        signals = [signals]

    # Deterministic selection priority
    chosen = None
    if any("flaky" in s for s in signals):
        chosen = "flaky_tests"
    elif any("refactor" in s for s in signals):
        chosen = "big_refactor"
    elif any("privacy" in s or "security" in s for s in signals):
        chosen = "security_privacy"
    else:
        chosen = "big_refactor" if inputs.get("risk") in ("high","critical") else "flaky_tests"

    tpl = TEMPLATES[chosen]
    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"edge_case_selector",
        "status":"ok",
        "outputs":{
            "template": chosen,
            "evidence_required": tpl["evidence_required"],
            "notes": tpl["notes"]
        },
        "metrics":{},
        "errors":[],
        "warnings":[]
    }
