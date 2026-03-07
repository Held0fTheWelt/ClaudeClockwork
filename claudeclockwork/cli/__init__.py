"""Phase 28 — CLI package: main entry, first-run, env-check."""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.core.executor.pipeline import ExecutionPipeline
from claudeclockwork.runtime import build_executor, build_planner, build_plugin_registry


def _run_plugin_healthcheck(plugin_id: str, project_root: Path) -> int:
    registry = build_plugin_registry(project_root)
    manifest = registry.get_manifest(plugin_id)
    if manifest is None:
        print(json.dumps({"status": "fail", "errors": [f"Unknown plugin: {plugin_id!r}"]}))
        return 1
    hook = manifest.lifecycle.get("healthcheck")
    if not hook:
        print(json.dumps({"status": "ok", "plugin": plugin_id, "detail": "no healthcheck hook declared"}))
        return 0
    try:
        module_path, fn_name = hook.rsplit(":", 1)
        module = importlib.import_module(module_path)
        fn = getattr(module, fn_name)
        result = fn()
        ok = result is None or bool(result)
        print(json.dumps({"status": "ok" if ok else "fail", "plugin": plugin_id, "detail": str(result)}))
        return 0 if ok else 1
    except Exception as exc:
        print(json.dumps({"status": "fail", "plugin": plugin_id, "errors": [str(exc)]}))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="ClaudeClockwork Full Skill System CLI")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--skill-id", default="")
    parser.add_argument("--user-input", default="")
    parser.add_argument("--inputs", default="{}", help="JSON object for skill inputs")
    parser.add_argument("--plugin-healthcheck", default="", metavar="PLUGIN_ID",
                        help="Run the healthcheck hook for the named plugin")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    subparsers.add_parser("first-run", help="Create runtime root, validate (Phase 28)")
    subparsers.add_parser("env-check", help="Verify environment (Phase 28)")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    inputs = json.loads(args.inputs)

    if args.command == "first-run":
        from claudeclockwork.cli.first_run import run_first_run
        result = run_first_run(project_root)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "env-check":
        from claudeclockwork.cli.env_check import run_env_check
        code, errors, info = run_env_check(project_root)
        print(json.dumps({"ok": code == 0, "errors": errors, "info": info}, indent=2))
        return code

    if args.plugin_healthcheck:
        return _run_plugin_healthcheck(args.plugin_healthcheck, project_root)

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


__all__ = ["main"]
