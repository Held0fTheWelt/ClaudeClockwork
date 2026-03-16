#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

REQUIRED_AGENT_FILES = [
    "agents/team_lead.md",
    "agents/designer.md",
    "agents/specialists.md",
    "agents/research.md",
    "agents/skill_dispatcher.md",
    "agents/tester.md",
    "agents/librarian.md",
]

REQUIRED_AGENT_DIRS = [
    "agents/critics",
    "agents/learning",
    "agents/operations",
    "agents/testops",
    "agents/workers",
]

REQUIRED_WORKERS = [
    "agents/workers/implementation_worker.md",
    "agents/workers/report_worker.md",
]

REQUIRED_TESTOPS = [
    "agents/testops/testops_orchestrator.md",
    "agents/testops/testrunner_light.md",
    "agents/testops/testrunner_medium.md",
    "agents/testops/testrunner_heavy.md",
]


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    claude_root = Path(inputs.get("claude_root", ".claude")).resolve()

    missing_files = [p for p in (REQUIRED_AGENT_FILES + REQUIRED_WORKERS + REQUIRED_TESTOPS) if not (claude_root / p).exists()]
    missing_dirs = [p for p in REQUIRED_AGENT_DIRS if not (claude_root / p).exists()]

    critic_files = list((claude_root / "agents/critics").glob("*.md")) if (claude_root / "agents/critics").exists() else []
    learning_files = list((claude_root / "agents/learning").glob("*.md")) if (claude_root / "agents/learning").exists() else []

    issues = []
    if not critic_files:
        issues.append("No critic definitions found under agents/critics/")
    if not learning_files:
        issues.append("No learning agents found under agents/learning/")

    status = "ok" if (not missing_files and not missing_dirs and not issues) else "fail"

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "team_topology_verify"),
        "status": status,
        "outputs": {
            "claude_root": str(claude_root),
            "missing_files": missing_files,
            "missing_dirs": missing_dirs,
            "issues": issues,
            "critic_count": len(critic_files),
            "learning_count": len(learning_files),
        },
        "metrics": {
            "missing_files": len(missing_files),
            "missing_dirs": len(missing_dirs),
            "issues": len(issues),
            "critic_count": len(critic_files),
            "learning_count": len(learning_files),
        },
        "errors": ["Team topology verification failed"] if status == "fail" else [],
        "warnings": [],
    }
