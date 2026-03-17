"""Wave 1: VERSION management using system contract canonical location."""
import yaml
from pathlib import Path
from typing import Tuple, List


class VersionManager:
    """Manage VERSION files using system contract as SSOT."""

    CONFIG_PATH = Path(".claude/system_contract.yaml")

    @classmethod
    def load_contract(cls) -> dict:
        """Load the system contract from YAML file."""
        if not cls.CONFIG_PATH.exists():
            raise FileNotFoundError(f"Configuration file {cls.CONFIG_PATH} does not exist.")

        with open(cls.CONFIG_PATH, 'r') as file:
            return yaml.safe_load(file)

    @classmethod
    def get_canonical_version_path(cls) -> str:
        """Get canonical VERSION location from system contract."""
        contract = cls.load_contract()
        canonical_path = contract.get('canonical_version_location')

        if not canonical_path:
            raise ValueError("canonical_version_location not defined in system contract")

        return canonical_path

    @classmethod
    def get_canonical_version(cls, project_root: Path) -> str:
        """Read the canonical version from the location specified in the contract."""
        canonical_path_str = cls.get_canonical_version_path()
        canonical_path = project_root / canonical_path_str

        if not canonical_path.exists():
            raise FileNotFoundError(f"Canonical version file {canonical_path} does not exist.")

        with open(canonical_path, 'r') as file:
            return file.read().strip()

    @classmethod
    def check_drift(cls, project_root: Path) -> Tuple[bool, List[str]]:
        """Compare versions and return consistency status."""
        errors = []
        is_consistent = True

        try:
            canonical_version = cls.get_canonical_version(project_root)
        except Exception as e:
            errors.append(str(e))
            return False, errors

        # Check root VERSION file
        root_version_path = project_root / "VERSION"

        if root_version_path.exists():
            with open(root_version_path, 'r') as file:
                root_version = file.read().strip()

            if root_version != canonical_version:
                errors.append(f"VERSION drift: root={root_version}, canonical={canonical_version}")
                is_consistent = False

        return is_consistent, errors

    @classmethod
    def fix_drift(cls, project_root: Path) -> bool:
        """Update root VERSION to match canonical version."""
        try:
            canonical_version = cls.get_canonical_version(project_root)
            root_version_path = project_root / "VERSION"

            with open(root_version_path, 'w') as file:
                file.write(canonical_version)

            return True
        except Exception as e:
            print(f"Error fixing VERSION drift: {e}")
            return False
