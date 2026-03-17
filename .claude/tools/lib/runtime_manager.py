from pathlib import Path
from typing import List, Tuple, Dict

def get_runtime_artifact_dirs(project_root: Path) -> List[Path]:
    """
    Get runtime artifact directories for a given project root.

    Args:
        project_root (Path): The root directory of the project.

    Returns:
        List[Path]: A list containing paths to the '.report' and 
                    '.clockwork_runtime' directories.
    """
    return [project_root / '.report', project_root / '.clockwork_runtime']


def ensure_runtime_dirs_exist(project_root: Path, contract: Dict) -> bool:
    """
    Ensure that runtime directories exist based on the contract settings.

    Args:
        project_root (Path): The root directory of the project.
        contract (Dict): Contract dictionary containing configuration options.

    Returns:
        bool: True if directories were ensured to exist or already existed.

    Raises:
        RuntimeError: If ensuring directories exist fails due to unexpected errors.
    """
    artifact_dirs = get_runtime_artifact_dirs(project_root)
    
    try:
        if not contract.get('auto_create_runtime_dirs'):
            return True
        
        for dir_path in artifact_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return True
    except Exception as e:
        raise RuntimeError("Failed to ensure runtime directories existence") from e


def validate_runtime_artifacts(project_root: Path, mode: str, contract: Dict) -> Tuple[bool, List[str]]:
    """
    Validate runtime artifacts against the provided mode and contract.

    Args:
        project_root (Path): The root directory of the project.
        mode (str): The current mode to validate artifacts against.
        contract (Dict): Contract dictionary containing validation rules or settings.

    Returns:
        Tuple[bool, List[str]]: A tuple where the first element is a boolean indicating 
                                if all artifacts are valid and the second element is a list of error messages.

    """
    artifact_names = ['.report', '.clockwork_runtime']
    errors = []

    for artifact_name in artifact_names:
        dir_path = project_root / artifact_name
        if dir_path.exists():
            from artifact_policy import is_valid_artifact
            if not is_valid_artifact(artifact_name, mode):
                errors.append(f"Artifact {artifact_name} invalid in {mode}")

    return (len(errors) == 0, errors)


def init_runtime_environment(project_root: Path, contract: Dict) -> None:
    """
    Initialize the runtime environment for a project.

    Args:
        project_root (Path): The root directory of the project.
        contract (Dict): Contract dictionary containing configuration options.

    Raises:
        RuntimeError: If runtime validation fails or an error occurs during initialization.
    """
    from system_contract import detect_package_mode

    mode = detect_package_mode(str(project_root), contract)
    ensure_runtime_dirs_exist(project_root, contract)
    
    valid, errors = validate_runtime_artifacts(project_root, mode, contract)
    if not valid:
        raise RuntimeError(f"Runtime validation failed: {errors}")
