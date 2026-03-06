from __future__ import annotations

import argparse
import json
from pathlib import Path

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.core.executor.pipeline import ExecutionPipeline
from claudeclockwork.runtime import build_executor, build_planner


def main() -> int:
    parser = argparse.ArgumentParser(description="ClaudeClockwork Full Skill System CLI")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--skill-id", default="")
    parser.add_argument("--user-input", default="")
    parser.add_argument("--inputs", default="{}", help="JSON object for skill inputs")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    inputs = json.loads(args.inputs)

    if args.skill_id:
        req = {"request_id": "cli", "skill_id": args.skill_id, "inputs": inputs}
        result = run_manifest_skill(req, project_root)
        if result is None:
            print(json.dumps({"status": "fail", "errors": [f"Unknown skill_id: {args.skill_id}"]}, indent=2))
            return 1
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("status") == "ok" else 1

    pipeline = ExecutionPipeline(build_planner(project_root), build_executor(project_root), working_directory=str(project_root))
    result = pipeline.run(args.user_input, **inputs)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
