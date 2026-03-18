#!/usr/bin/env python3
"""
boot_check.py — System Contract Aware Boot Check

Validates package structure using canonical system contract.
Exit code 0 if all checks pass, 1 if any fail.
"""

import os
import sys
from pathlib import Path

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
        canonical_version = VersionManager.get_canonical_version(Path(PROJECT_ROOT))
        is_consistent, errors = VersionManager.check_drift(Path(PROJECT_ROOT))

        if is_consistent:
            return True, f"[PASS] VERSION {canonical_version} (canonical, no drift)"
        else:
            error_msg = "; ".join(errors) if errors else "VERSION mismatch detected"
            return False, f"[FAIL] {error_msg}"
    except Exception as e:
        return False, f"[FAIL] Error checking VERSION: {e}"

def check_runtime_artifacts(mode: str) -> tuple[bool, str]:
    """Verify runtime artifacts are valid for the current mode."""
    try:
        contract = load_contract(os.path.join(PROJECT_ROOT, ".claude", "system_contract.yaml"))
        from runtime_manager import validate_runtime_artifacts
        valid, errors = validate_runtime_artifacts(Path(PROJECT_ROOT), mode, contract)
        if valid:
            return True, "[PASS] Runtime artifacts are valid"
        else:
            error_str = "; ".join(errors) if errors else "validation failed"
            return False, f"[FAIL] Runtime artifacts invalid: {error_str}"
    except Exception as e:
        return False, f"[FAIL] Error checking runtime artifacts: {e}"

def check_model_runtime_policy() -> tuple[bool, str]:
    """Verify model runtime policy configuration is valid."""
    try:
        from model_runtime_policy import load_runtime_config
        config_path = os.path.join(PROJECT_ROOT, ".claude", "config", "local_ollama_runtime.yaml")
        config = load_runtime_config(config_path)
        
        if config:
            return True, "[PASS] Model runtime policy configuration is valid"
        else:
            return False, "[FAIL] Model runtime policy configuration is empty"
    except FileNotFoundError as e:
        return False, f"[FAIL] Model runtime config not found: {e}"
    except Exception as e:
        return False, f"[FAIL] Error validating model runtime policy: {e}"

def check_skill_registry(contract: dict) -> tuple[bool, str]:
    """Verify skill registry is valid and accessible."""
    try:
        from skill_registry import load_skill_registry, validate_all_skills
        
        skills = load_skill_registry(contract, Path(PROJECT_ROOT))
        
        if not skills:
            return False, "[FAIL] No skills found in registry"
        
        valid, errors = validate_all_skills(contract, Path(PROJECT_ROOT))
        
        if valid:
            return True, f"[PASS] Skill registry valid ({len(skills)} skills)"
        else:
            error_str = "; ".join(errors[:2])
            return False, f"[FAIL] Skill validation errors: {error_str}"
    except Exception as e:
        return False, f"[FAIL] Error checking skill registry: {e}"

def check_manifests(contract: dict) -> tuple[bool, str]:
    """Verify all skill manifests are valid."""
    try:
        from skill_registry import load_skill_registry
        from manifest_loader import load_all_manifests, validate_manifest_schema
        
        skills = load_skill_registry(contract, Path(PROJECT_ROOT))
        manifests = load_all_manifests(skills)
        
        errors = []
        for skill_id, (manifest, load_errors) in manifests.items():
            if load_errors:
                errors.extend([f"{skill_id}: {e}" for e in load_errors])
            else:
                valid, schema_errors = validate_manifest_schema(manifest, contract)
                if not valid:
                    errors.extend([f"{skill_id}: {e}" for e in schema_errors])
        
        if errors:
            error_str = "; ".join(errors[:2])
            return False, f"[FAIL] Manifest errors: {error_str}"
        else:
            return True, "[PASS] All skill manifests are valid"
    except Exception as e:
        return False, f"[FAIL] Error checking manifests: {e}"

def check_governance_protocol() -> tuple[bool, str]:
    """Verify governance protocol is valid and consistent."""
    try:
        from governance_manager import load_governance_protocol, check_governance_consistency
        
        config_path = os.path.join(PROJECT_ROOT, ".claude", "governance_protocol.yaml")
        protocol = load_governance_protocol(config_path)
        
        if not protocol:
            return False, "[FAIL] Governance protocol is empty"
        
        valid, errors = check_governance_consistency(protocol)
        
        if valid:
            num_roles = len(protocol.get('roles', []))
            return True, f"[PASS] Governance protocol valid ({num_roles} roles)"
        else:
            error_str = "; ".join(errors[:2])
            return False, f"[FAIL] Governance errors: {error_str}"
    except FileNotFoundError:
        return False, "[FAIL] Governance protocol not found"
    except Exception as e:
        return False, f"[FAIL] Error checking governance: {e}"

def check_role_permissions() -> tuple[bool, str]:
    """Verify all role-permission assignments are valid."""
    try:
        from governance_manager import load_governance_protocol, validate_role_permissions
        
        config_path = os.path.join(PROJECT_ROOT, ".claude", "governance_protocol.yaml")
        protocol = load_governance_protocol(config_path)
        
        valid, errors = validate_role_permissions(protocol)
        
        if valid:
            num_assignments = len(protocol.get('role_permissions', {}))
            return True, f"[PASS] All role-permissions valid ({num_assignments} roles)"
        else:
            error_str = "; ".join(errors[:2])
            return False, f"[FAIL] Role-permission errors: {error_str}"
    except Exception as e:
        return False, f"[FAIL] Error checking role permissions: {e}"

def check_execution_framework() -> tuple[bool, str]:
    """Verify execution framework YAML is valid and contains all required sections."""
    try:
        import yaml
        config_path = os.path.join(PROJECT_ROOT, ".claude", "execution_framework.yaml")
        with open(config_path, "r") as f:
            yaml_content = yaml.safe_load(f)
        
        framework = yaml_content.get("execution_framework", {})
        
        if not framework:
            return False, "[FAIL] Execution framework is empty"
        
        required_sections = ["agents", "task_templates", "workflow_definitions", "quality_gates", "performance_budgets"]
        missing = [s for s in required_sections if s not in framework or not framework[s]]
        
        if missing:
            return False, f"[FAIL] Execution framework missing sections: {', '.join(missing)}"
        
        return True, "[PASS] Execution framework valid (5 sections present)"
    except FileNotFoundError:
        return False, "[FAIL] Execution framework file not found"
    except Exception as e:
        return False, f"[FAIL] Error validating execution framework: {e}"

def check_execution_consistency() -> tuple[bool, str]:
    """Verify execution framework is internally consistent."""
    try:
        import yaml
        from execution_manager import check_execution_consistency as check_consistency
        
        config_path = os.path.join(PROJECT_ROOT, ".claude", "execution_framework.yaml")
        with open(config_path, "r") as f:
            yaml_content = yaml.safe_load(f)
        
        framework = yaml_content.get("execution_framework", {})
        
        if not framework:
            return False, "[FAIL] Framework not found in YAML"
        
        valid, errors = check_consistency(framework)
        
        if valid:
            return True, "[PASS] Execution framework consistent"
        else:
            error_str = "; ".join(errors[:2]) if errors else "consistency check failed"
            return False, f"[FAIL] Execution consistency: {error_str}"
    except Exception as e:
        return False, f"[FAIL] Error checking execution consistency: {e}"

def check_manifest_mode_drift(contract: dict) -> tuple[bool, str]:
    """Verify all skill manifests have valid mode_requirements metadata."""
    try:
        from skill_registry import load_skill_registry
        from manifest_loader import load_all_manifests
        
        skills = load_skill_registry(contract, Path(PROJECT_ROOT))
        manifests = load_all_manifests(skills)
        
        errors = []
        valid_types = {'local', 'ollama', 'claude', 'hybrid'}
        
        for skill_id, (manifest, load_errors) in manifests.items():
            if load_errors:
                continue
            metadata = manifest.get('metadata', {})
            mode_req = metadata.get('mode_requirements')
            if not mode_req:
                errors.append(f"{skill_id}: missing mode_requirements")
            elif mode_req.get('agent_type') not in valid_types:
                agent_type = mode_req.get('agent_type')
                errors.append(f"{skill_id}: unsupported agent_type '{agent_type}'")
        
        if errors:
            msg = f"[FAIL] Manifest mode drift: {len(errors)} invalid\n"
            for e in errors[:10]:
                msg += f"  {e}\n"
            msg += f"Summary: Fix {len(errors)} manifest(s)"
            return False, msg
        
        return True, "[PASS] All manifests have valid mode_requirements"
    except Exception as e:
        return False, f"[FAIL] Mode drift check error: {e}"



def main() -> int:
    print("=== Clockwork Boot Check (Contract-Aware) ===")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    all_pass = True

    # Load contract for later use
    contract = load_contract(os.path.join(PROJECT_ROOT, ".claude", "system_contract.yaml"))

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

    # Check 5: Runtime artifacts (contract-driven)
    if mode:
        ok, msg = check_runtime_artifacts(mode)
        print(msg)
        if not ok:
            all_pass = False

    # Check 6: Model runtime policy
    ok, msg = check_model_runtime_policy()
    print(msg)
    if not ok:
        all_pass = False

    # Check 7: Skill registry
    ok, msg = check_skill_registry(contract)
    print(msg)
    if not ok:
        all_pass = False

    # Check 8: Manifest validity
    ok, msg = check_manifests(contract)
    print(msg)
    if not ok:
        all_pass = False

    # Check 13: Manifest mode drift
    ok, msg = check_manifest_mode_drift(contract)
    print(msg)
    if not ok:
        all_pass = False

    # Check 9: Governance protocol
    ok, msg = check_governance_protocol()
    print(msg)
    if not ok:
        all_pass = False

    # Check 10: Role permissions
    ok, msg = check_role_permissions()
    print(msg)
    if not ok:
        all_pass = False

    # Check 11: Execution framework
    ok, msg = check_execution_framework()
    print(msg)
    if not ok:
        all_pass = False

    # Check 12: Execution consistency
    ok, msg = check_execution_consistency()
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
