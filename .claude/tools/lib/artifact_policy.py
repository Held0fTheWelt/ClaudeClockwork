import yaml
from typing import Dict, Any

class ArtifactPolicyError(Exception):
    """Custom exception for artifact policy errors."""
    pass


def load_system_contract(file_path: str) -> Dict[str, Any]:
    """
    Load the system contract from a YAML file.

    Args:
        file_path (str): Path to the system contract YAML file.

    Returns:
        dict: Parsed YAML content as a dictionary.

    Raises:
        ArtifactPolicyError: If there is an error loading or parsing the YAML.
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise ArtifactPolicyError(f"System contract file not found: {file_path}")
    except yaml.YAMLError as e:
        raise ArtifactPolicyError(f"Error parsing YAML file: {e}")


def is_valid_artifact(artifact_name: str, mode: str) -> bool:
    """
    Determine if an artifact is valid based on the current mode.

    Args:
        artifact_name (str): Name of the artifact.
        mode (str): Current mode ('repo_mode' or 'claude_only_mode').

    Returns:
        bool: True if the artifact is valid, False otherwise.
    """
    if mode not in ['repo_mode', 'claude_only_mode']:
        raise ArtifactPolicyError(f"Invalid mode: {mode}")

    # Define curated artifacts
    curated_artifacts = {
        '.report': 'curated-only',
        '.clockwork_runtime': 'auto-creatable'
    }

    artifact_type = curated_artifacts.get(artifact_name, None)

    if mode == 'claude_only_mode':
        return artifact_type == 'curated-only'

    # In repo_mode, only reject auto-generated artifacts
    if artifact_type == 'auto-creatable':
        return True

    return artifact_type is not None


def main():
    """
    Main function to demonstrate loading the system contract and validating artifacts.
    """
    try:
        system_contract = load_system_contract('.claude/tools/lib/system_contract.yaml')
        print("System Contract Loaded:", system_contract)

        # Example usage
        artifact_name = '.report'
        mode = 'repo_mode'

        if is_valid_artifact(artifact_name, mode):
            print(f"Artifact '{artifact_name}' is valid in {mode}.")
        else:
            print(f"Artifact '{artifact_name}' is invalid in {mode}.")

    except ArtifactPolicyError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()