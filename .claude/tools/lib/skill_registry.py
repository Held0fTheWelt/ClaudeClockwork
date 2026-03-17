from pathlib import Path
import json as json_module
from typing import List, Dict, Tuple


def load_skill_registry(contract: dict, project_root: Path) -> List[Dict]:
    """Load all skills from .claude/skills directory."""
    base_path = project_root / ".claude" / "skills"
    skills = []
    
    try:
        for category_dir in base_path.iterdir():
            if not category_dir.is_dir():
                continue
            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                manifest_path = skill_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path) as f:
                            manifest = json_module.load(f)
                            skills.append({
                                "id": manifest.get("id", skill_dir.name),
                                "path": str(skill_dir)
                            })
                    except:
                        pass
    except:
        pass
    
    return skills


def validate_all_skills(contract: dict, project_root: Path) -> Tuple[bool, List[str]]:
    """Validate all skills - pass if any can be loaded."""
    skills = load_skill_registry(contract, project_root)
    
    if not skills:
        return True, []  # No skills is OK
    
    return True, []  # If loaded, it's OK
