"""
Clockwork tooling library — shared utilities for .claude/tools scripts.
"""

from .system_contract import (
    load_contract,
    validate_package_mode,
    validate_repo_structure,
    get_canonical_version_path,
    get_runtime_artifact_dirs,
    detect_package_mode,
)

__all__ = [
    "load_contract",
    "validate_package_mode",
    "validate_repo_structure",
    "get_canonical_version_path",
    "get_runtime_artifact_dirs",
    "detect_package_mode",
]
