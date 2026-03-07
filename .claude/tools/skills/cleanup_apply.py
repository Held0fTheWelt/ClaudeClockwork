#!/usr/bin/env python3
"""
cleanup_apply — CCW-MVP13 Cleaning Suite skill.

Applies a cleanup plan (JSON) to the filesystem.

Usage (standalone):
    python cleanup_apply.py '{"skill_id":"cleanup_apply","inputs":{"plan_path":"plan.json","dry_run":true}}'
    echo '{"skill_id":"cleanup_apply","inputs":{"root":".","dry_run":true}}' | python cleanup_apply.py

Usage (via skill_runner):
    The run(req) interface is called with a SkillRequestSpec dict.

Inputs:
    plan_path    (str)  — path or glob pattern to a JSON plan file.
                          Plan format: {"operations": [{"action": "move"|"delete"|"archive"|"rename",
                                                         "source": str, "dest": str (optional)}]}
    root         (str)  — repo root for path resolution; default "."
    dry_run      (bool) — default True; when True, no filesystem changes are made
    allow_delete (bool) — default False; when False, delete operations are skipped with a warning
    on_conflict  (str)  — "skip"|"overwrite"|"rename"; default "skip"
    write_report (bool) — default False; when True, write report JSON to report_dir
    report_dir   (str)  — destination folder for reports; default ".clockwork_runtime/knowledge/writes/clean_reports"

Output (skill_result_spec):
    {
      "type": "skill_result_spec",
      "status": "ok" | "error",
      "outputs": {
        "operations": [...],
        "summary": {"moved": N, "deleted": N, "skipped": N, "missing": N, "errors": N, "total": N},
        "dry_run": bool
      }
    }
"""

from __future__ import annotations

import glob as _glob
import json
import os
import shutil
import sys
from pathlib import Path

_LIMITATIONS = [
    "dry_run=True by default — safety first; no filesystem changes made unless dry_run=False.",
    "allow_delete=False by default; delete ops are silently skipped unless explicitly enabled.",
    "Operations are executed in order; earlier moves may affect later path resolution.",
    "Paths outside root are refused for security.",
    "Supported actions: move, delete, archive, rename.",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_plan(root: Path, plan_path_pattern: str) -> tuple[dict, str]:
    """Load JSON plan from path or glob pattern. Returns (plan_dict, resolved_path_str)."""
    p = Path(plan_path_pattern)
    if p.exists():
        resolved = p.resolve()
    else:
        # Try relative to root first, then as a bare glob
        candidates = _glob.glob(str((root / plan_path_pattern).resolve()))
        if not candidates:
            candidates = _glob.glob(plan_path_pattern)
        if not candidates:
            raise FileNotFoundError(f"No plan file matches: {plan_path_pattern!r}")
        candidates.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
        resolved = Path(candidates[0]).resolve()
    plan = json.loads(resolved.read_text(encoding="utf-8"))
    return plan, str(resolved)


def _within_root(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def _abs_path(root: Path, src: str) -> Path:
    p = Path(src)
    return p.resolve() if p.is_absolute() else (root / p).resolve()


def _conflict_dst(dst_abs: Path, on_conflict: str) -> tuple[Path | None, str | None]:
    """
    Return (resolved_dst, skip_reason).  skip_reason is non-None when we should skip.
    """
    if not dst_abs.exists():
        return dst_abs, None
    if on_conflict == "skip":
        return None, f"destination exists; on_conflict=skip"
    if on_conflict == "overwrite":
        return dst_abs, None
    if on_conflict == "rename":
        base = dst_abs
        k = 1
        while dst_abs.exists():
            dst_abs = base.with_name(base.name + f".{k}")
            k += 1
        return dst_abs, None
    return None, f"unknown on_conflict={on_conflict!r}; skipping"


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root", ".")).resolve()
    plan_path_input: str | None = inputs.get("plan_path")
    plan_inline: dict | None = inputs.get("plan")
    dry_run: bool = bool(inputs.get("dry_run", True))
    allow_delete: bool = bool(inputs.get("allow_delete", False))
    on_conflict: str = str(inputs.get("on_conflict", "skip")).lower()
    write_report: bool = bool(inputs.get("write_report", False))
    report_dir: Path = (root / (inputs.get("report_dir") or ".clockwork_runtime/knowledge/writes/clean_reports")).resolve()

    warnings: list[str] = []

    # ---- Load plan ----
    plan_path_resolved: str | None = None
    if plan_inline is not None:
        plan = plan_inline
    elif plan_path_input:
        try:
            plan, plan_path_resolved = _resolve_plan(root, plan_path_input)
        except FileNotFoundError as exc:
            # Missing plan file is handled gracefully: return summary with 0 ops
            warnings.append(str(exc))
            plan = {"operations": []}
        except (json.JSONDecodeError, OSError) as exc:
            return _error(req, f"Failed to load plan: {exc}")
    else:
        return _error(req, "Provide either inputs.plan (dict) or inputs.plan_path (str).")

    raw_ops: list[dict] = plan.get("operations", []) or []

    # ---- Process operations ----
    results: list[dict] = []
    moved = deleted = skipped = missing = errors = 0

    for op in raw_ops:
        action = (op.get("action") or op.get("op") or "").lower()
        source_str: str = str(op.get("source") or op.get("src") or "")
        dest_str: str = str(op.get("dest") or op.get("dst") or "")

        if not source_str:
            results.append({"action": action, "source": source_str, "dest": dest_str,
                             "status": "error", "message": "missing source field"})
            errors += 1
            continue

        src_abs = _abs_path(root, source_str)

        # Security: refuse paths outside root
        if not _within_root(root, src_abs):
            results.append({"action": action, "source": source_str, "dest": dest_str,
                             "status": "skipped", "message": "source is outside root; refused"})
            skipped += 1
            continue

        if not src_abs.exists():
            results.append({"action": action, "source": source_str, "dest": dest_str,
                             "status": "missing", "message": "source path does not exist"})
            missing += 1
            continue

        # ---- delete / archive / move / rename ----
        if action == "delete":
            if not allow_delete:
                results.append({"action": action, "source": source_str, "dest": "",
                                 "status": "skipped", "message": "delete skipped (allow_delete=False)"})
                skipped += 1
                warnings.append(f"Delete skipped for {source_str!r} — set allow_delete=True to enable.")
                continue
            if dry_run:
                results.append({"action": action, "source": source_str, "dest": "",
                                 "status": "planned", "message": "dry_run"})
            else:
                try:
                    if src_abs.is_dir():
                        shutil.rmtree(src_abs)
                    else:
                        src_abs.unlink()
                    results.append({"action": action, "source": source_str, "dest": "",
                                     "status": "deleted", "message": "deleted"})
                    deleted += 1
                except OSError as exc:
                    results.append({"action": action, "source": source_str, "dest": "",
                                     "status": "error", "message": str(exc)})
                    errors += 1

        elif action in ("move", "archive", "rename"):
            if not dest_str:
                results.append({"action": action, "source": source_str, "dest": "",
                                 "status": "error", "message": f"action={action!r} requires a dest"})
                errors += 1
                continue

            dst_abs = _abs_path(root, dest_str)
            if not _within_root(root, dst_abs):
                results.append({"action": action, "source": source_str, "dest": dest_str,
                                 "status": "skipped", "message": "destination is outside root; refused"})
                skipped += 1
                continue

            final_dst, skip_reason = _conflict_dst(dst_abs, on_conflict)
            if skip_reason:
                results.append({"action": action, "source": source_str, "dest": dest_str,
                                 "status": "skipped", "message": skip_reason})
                skipped += 1
                continue

            if dry_run:
                results.append({"action": action, "source": source_str, "dest": dest_str,
                                 "status": "planned", "message": "dry_run"})
            else:
                try:
                    final_dst.parent.mkdir(parents=True, exist_ok=True)
                    if on_conflict == "overwrite" and final_dst.exists():
                        if final_dst.is_dir():
                            shutil.rmtree(final_dst)
                        else:
                            final_dst.unlink()
                    shutil.move(str(src_abs), str(final_dst))
                    results.append({"action": action, "source": source_str, "dest": str(final_dst),
                                     "status": "moved", "message": "moved"})
                    moved += 1
                except OSError as exc:
                    results.append({"action": action, "source": source_str, "dest": dest_str,
                                     "status": "error", "message": str(exc)})
                    errors += 1
        else:
            results.append({"action": action, "source": source_str, "dest": dest_str,
                             "status": "skipped", "message": f"unsupported action: {action!r}"})
            skipped += 1

    # In dry_run mode, nothing actually moved/deleted
    if dry_run:
        moved = deleted = 0

    total = len(results)
    import datetime as _dt
    now = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    summary = {
        "total": total,
        "moved": moved,
        "deleted": deleted,
        "skipped": skipped,
        "missing": missing,
        "errors": errors,
    }

    report_json_path: str | None = None
    if write_report and not dry_run or (write_report):
        try:
            report_dir.mkdir(parents=True, exist_ok=True)
            ts = now.replace(":", "").replace("-", "")
            rp = report_dir / f"cleanup_apply_report_{ts}.json"
            report_payload = {
                "type": "cleanup_apply_report",
                "generated_at": now,
                "dry_run": dry_run,
                "operations": results,
                "summary": summary,
                "warnings": warnings + ([f"plan_path={plan_path_resolved}"] if plan_path_resolved else []),
                "limitations": _LIMITATIONS,
            }
            rp.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            report_json_path = str(rp)
        except OSError as exc:
            warnings.append(f"Failed to write report: {exc}")

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "cleanup_apply",
        "status": "ok",
        "outputs": {
            "operations": results,
            "summary": summary,
            "dry_run": dry_run,
            "report_json_path": report_json_path,
        },
        "errors": [],
        "warnings": warnings,
        "metrics": summary,
    }


def _error(req: dict, msg: str) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "cleanup_apply",
        "status": "error",
        "outputs": {},
        "errors": [msg],
        "warnings": [],
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

    # Accept both bare input dict and wrapped SkillRequestSpec
    if data.get("type") == "skill_request_spec" or data.get("skill_id") == "cleanup_apply":
        result = run(data)
    else:
        # Bare inputs dict
        result = run({"skill_id": "cleanup_apply", "inputs": data})

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
