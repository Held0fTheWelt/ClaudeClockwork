"""
System Contract Loader — unified source of truth for ClaudeClockwork configuration.

Provides functions to load and validate the canonical system contract (.claude/system_contract.yaml).
All tools that check package structure, runtime paths, or version locations must use this module
instead of hardcoding their own assumptions.
"""

import yaml
import os
from typing import Dict, Tuple, List


def load_contract(contract_path: str = None) -> Dict:
    """
    Load the system contract YAML file and return its contents as a dictionary.

    Args:
        contract_path: Path to system_contract.yaml. If None, uses ./.claude/system_contract.yaml

    Returns:
        dict: Parsed contract with keys like canonical_version_location, supported_package_modes, etc.

    Raises:
        FileNotFoundError: If contract file not found
        yaml.YAMLError: If contract YAML is invalid
    """
    if contract_path is None:
        contract_path = os.path.join(os.path.dirname(__file__), '..', '..', 'system_contract.yaml')

    contract_path = os.path.abspath(contract_path)

    if not os.path.exists(contract_path):
        raise FileNotFoundError(f"System contract not found at {contract_path}")

    with open(contract_path, 'r') as f:
        return yaml.safe_load(f)


def validate_package_mode(mode: str, contract: Dict) -> bool:
    """
    Check if the given package mode is supported by the contract.

    Args:
        mode: Package mode name (e.g., "repo_mode", "claude_only_mode")
        contract: Loaded contract dict

    Returns:
        True if mode is supported, False otherwise
    """
    return mode in contract.get('supported_package_modes', [])


def validate_repo_structure(repo_root: str, mode: str, contract: Dict) -> Tuple[bool, List[str]]:
    """
    Validate that all required paths for the given mode exist in the repository.

    Args:
        repo_root: Root directory of the repository
        mode: Package mode (e.g., "repo_mode", "claude_only_mode")
        contract: Loaded contract dict

    Returns:
        Tuple: (all_required_exist: bool, missing_required_paths: List[str])
    """
    if not validate_package_mode(mode, contract):
        raise ValueError(f"Unknown package mode: {mode}")

    # Get required paths for this mode (e.g., "repo_mode_required_paths")
    required_key = f"{mode}_required_paths"
    required_paths = contract.get(required_key, [])

    missing = []
    for path in required_paths:
        full_path = os.path.join(repo_root, path)
        if not os.path.exists(full_path):
            missing.append(path)

    return len(missing) == 0, missing


def get_canonical_version_path(contract: Dict) -> str:
    """
    Get the canonical version file path from the contract.

    Args:
        contract: Loaded contract dict

    Returns:
        str: Path to canonical VERSION file (relative to repo root, e.g., ".claude/VERSION")
    """
    return contract.get('canonical_version_location', '.claude/VERSION')


def get_runtime_artifact_dirs(contract: Dict, include_optional: bool = False) -> List[str]:
    """
    Get a list of runtime artifact directory names from the contract.

    Args:
        contract: Loaded contract dict
        include_optional: If True, return all artifact dirs. If False, only required ones.

    Returns:
        List[str]: Directory names like [".report", ".clockwork_runtime"]
    """
    runtime_artifacts = contract.get('runtime_artifacts', {})

    # All artifact directory names (keys)
    return list(runtime_artifacts.keys()) if isinstance(runtime_artifacts, dict) else []


def detect_package_mode(repo_root: str, contract: Dict) -> str:
    """
    Auto-detect package mode by checking which required paths exist.

    Args:
        repo_root: Root directory of the repository
        contract: Loaded contract dict

    Returns:
        str: Detected mode name (e.g., "repo_mode" or "claude_only_mode")

    Raises:
        ValueError: If repo structure doesn't match any known mode
    """
    for mode in contract.get('supported_package_modes', []):
        passed, _ = validate_repo_structure(repo_root, mode, contract)
        if passed:
            return mode

    raise ValueError(f"Repository structure does not match any supported package mode")
