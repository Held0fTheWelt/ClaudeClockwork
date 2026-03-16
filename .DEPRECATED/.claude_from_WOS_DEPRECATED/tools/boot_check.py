#!/usr/bin/env python3
"""
boot_check.py — CCW-MVP01 Boot Check
Validates that the required Clockwork paths and VERSION file are present.
Exit code 0 if all checks pass, 1 if any fail.
"""

import os
import sys

# Project root is two levels up from this file (.claude/tools/boot_check.py)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

REQUIRED_PATHS = [
    ".claude/INDEX.md",
    ".claude/SYSTEM.md",
    ".claude/skills/",
    ".claude/contracts/schemas/",
    ".claude/contracts/examples/",
    ".claude/governance/",
    ".claude/agents/",
    ".report/",
]

VERSION_FILE = "VERSION"


def check_path(rel_path: str) -> tuple[bool, str]:
    full = os.path.join(PROJECT_ROOT, rel_path)
    if rel_path.endswith("/"):
        exists = os.path.isdir(full)
        kind = "dir"
    else:
        exists = os.path.isfile(full)
        kind = "file"
    status = "PASS" if exists else "FAIL"
    return exists, f"[{status}] {rel_path} ({kind})"


def check_version() -> tuple[bool, str]:
    full = os.path.join(PROJECT_ROOT, VERSION_FILE)
    if not os.path.isfile(full):
        return False, f"[FAIL] {VERSION_FILE} (file) — not found"
    with open(full, "r", encoding="utf-8") as fh:
        contents = fh.read().strip()
    return True, f"[PASS] {VERSION_FILE} — {contents}"


def main() -> int:
    print("=== Clockwork Boot Check ===")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    all_pass = True

    for rel_path in REQUIRED_PATHS:
        ok, msg = check_path(rel_path)
        print(msg)
        if not ok:
            all_pass = False

    ok, msg = check_version()
    print(msg)
    if not ok:
        all_pass = False

    print()
    if all_pass:
        print("Result: ALL CHECKS PASSED")
        return 0
    else:
        print("Result: ONE OR MORE CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
