#!/usr/bin/env python3
"""
boot_check.py — System Contract Aware Boot Check

Validates package structure using canonical system contract.
Exit code 0 if all checks pass, 1 if any fail.
"""

import os
import sys

# Project root is two levels up from this file (.claude/tools/boot_check.py)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Import system contract loader and version manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from system_contract import (
    load_contract,
    detect_package_mode,
    validate_repo_structure,
    get_canonical_version_path,
    get_runtime_artifact_dirs,
)
from version_manager import VersionManager


def check_contract_loads() -> tuple[bool, str]:
    """Verify system contract exists and is valid."""
    try:
        contract = load_contract(os.path.join(PROJECT_ROOT, ".claude", "system_contract.yaml"))
        return True, "[PASS] System contract loaded successfully"
    except FileNotFoundError as e:
        return False, f"[FAIL] System contract not found: {e}"
    except Exception as e:
        return False, f"[FAIL] System contract invalid: {e}"


def check_package_mode() -> tuple[bool, str, str]:
    """Detect package mode (repo_mode or claude_only_mode)."""
    try:
        contract = load_contract(os.path.join(PROJECT_ROOT, ".claude", "system_contract.yaml"))
        mode = detect_package_mode(PROJECT_ROOT, contract)
        return True, f"[PASS] Detected package mode: {mode}", mode
    except ValueError as e:
        return False, f"[FAIL] {e}", ""
    except Exception as e:
        return False, f"[FAIL] Error detecting mode: {e}", ""


def check_required_paths(mode: str) -> tuple[bool, str]:
    """Validate all required paths for the detected mode exist."""
    try:
        contract = load_contract(os.path.join(PROJECT_ROOT, ".claude", "system_contract.yaml"))
        passed, missing = validate_repo_structure(PROJECT_ROOT, mode, contract)

        if passed:
            return True, f"[PASS] All required paths for {mode} exist"
        else:
            return False, f"[FAIL] Missing required paths for {mode}: {', '.join(missing)}"
    except Exception as e:
        return False, f"[FAIL] Error checking paths: {e}"


def check_version_file() -> tuple[bool, str]:
    """Verify VERSION file at canonical location and check for drift."""
    try:
        from pathlib import Path
        canonical_version = VersionManager.get_canonical_version(Path(PROJECT_ROOT))
        is_consistent, errors = VersionManager.check_drift(Path(PROJECT_ROOT))

        if is_consistent:
            return True, f"[PASS] VERSION {canonical_version} (canonical, no drift)"
        else:
            error_msg = "; ".join(errors) if errors else "VERSION mismatch detected"
            return False, f"[FAIL] {error_msg}"
    except Exception as e:
        return False, f"[FAIL] Error checking VERSION: {e}"


def main() -> int:
    print("=== Clockwork Boot Check (Contract-Aware) ===")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    all_pass = True

    # Check 1: Contract loads
    ok, msg = check_contract_loads()
    print(msg)
    if not ok:
        all_pass = False
        print()
        print("Result: BOOT CHECK FAILED (contract not found)")
        return 1

    # Check 2: Detect package mode
    ok, msg, mode = check_package_mode()
    print(msg)
    if not ok:
        all_pass = False

    # Check 3: Required paths (contract-driven)
    if mode:
        ok, msg = check_required_paths(mode)
        print(msg)
        if not ok:
            all_pass = False

    # Check 4: VERSION file at canonical location
    ok, msg = check_version_file()
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
