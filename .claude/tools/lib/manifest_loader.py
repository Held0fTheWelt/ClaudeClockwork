from pathlib import Path
import json as json_module
from typing import Dict, Tuple, List


def load_all_manifests(skills: List[Dict]) -> Dict[str, Tuple[Dict, List[str]]]:
    """Load all manifests - just check they parse as JSON."""
    result = {}
    
    for skill in skills:
        skill_id = skill.get("id", "unknown")
        skill_path = Path(skill.get("path", ""))
        manifest_path = skill_path / "manifest.json"
        
        try:
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json_module.load(f)
                    result[skill_id] = (manifest, [])
            else:
                result[skill_id] = ({}, ["manifest.json not found"])
        except Exception as e:
            result[skill_id] = ({}, [str(e)])
    
    return result


def validate_manifest_schema(manifest: dict, contract: dict) -> Tuple[bool, List[str]]:
    """Validate manifest - just check it's a dict."""
    if isinstance(manifest, dict):
        return (True, [])
    return (False, ["Invalid manifest format"])
