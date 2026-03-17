import yaml
from typing import Dict, Tuple, List


def load_governance_protocol(config_path: str) -> Dict:
    """
    Load governance_protocol.yaml.

    Args:
        config_path (str): Path to governance protocol file.

    Returns:
        Dict: Parsed governance protocol.

    Raises:
        FileNotFoundError: If file not found.
        yaml.YAMLError: If YAML parse error.
    """
    try:
        with open(config_path, 'r') as file:
            data = yaml.safe_load(file)
            return data.get('governance_protocol', {}) if isinstance(data, dict) else {}
    except FileNotFoundError:
        raise FileNotFoundError(f"Governance protocol not found: {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing governance protocol: {e}")


def validate_role_definitions(protocol: dict) -> Tuple[bool, List[str]]:
    """
    Validate all roles are properly defined.

    Args:
        protocol (dict): Governance protocol dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    required_fields = {'id', 'name', 'description', 'access_level'}
    
    for role in protocol.get('roles', []):
        missing = required_fields - set(role.keys())
        if missing:
            errors.append(f"Role missing {missing}")
    
    return len(errors) == 0, errors


def validate_permissions_matrix(protocol: dict) -> Tuple[bool, List[str]]:
    """
    Validate permissions are defined correctly.

    Args:
        protocol (dict): Governance protocol dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    
    permissions = protocol.get('permissions', {})
    if not permissions:
        errors.append("No permissions defined")
    
    for resource, perms in permissions.items():
        if not isinstance(perms, list) or len(perms) == 0:
            errors.append(f"Resource {resource} has no permissions")
    
    return len(errors) == 0, errors


def validate_role_permissions(protocol: dict) -> Tuple[bool, List[str]]:
    """
    Validate role-permission assignments.

    Args:
        protocol (dict): Governance protocol dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    role_ids = {r['id'] for r in protocol.get('roles', [])}
    valid_resources = set(protocol.get('permissions', {}).keys())
    
    for role_id, assignments in protocol.get('role_permissions', {}).items():
        if role_id not in role_ids:
            errors.append(f"Role {role_id} not defined")
        
        for resource, perms in assignments.items():
            if resource not in valid_resources:
                errors.append(f"Invalid resource {resource} for role {role_id}")
    
    return len(errors) == 0, errors


def check_governance_consistency(protocol: dict) -> Tuple[bool, List[str]]:
    """
    Check overall governance protocol consistency.

    Args:
        protocol (dict): Governance protocol dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    
    # Validate components
    valid, errs = validate_role_definitions(protocol)
    if not valid:
        errors.extend(errs)
    
    valid, errs = validate_permissions_matrix(protocol)
    if not valid:
        errors.extend(errs)
    
    valid, errs = validate_role_permissions(protocol)
    if not valid:
        errors.extend(errs)
    
    # Check decision protocols reference existing roles
    role_ids = {r['id'] for r in protocol.get('roles', [])}
    for dp in protocol.get('decision_protocols', []):
        for role_id in dp.get('approval_needed_by_roles', []):
            if role_id not in role_ids:
                errors.append(f"Decision protocol references undefined role {role_id}")
    
    return len(errors) == 0, errors


def get_role_permissions(role_id: str, protocol: dict) -> Dict:
    """
    Get permissions for a specific role.

    Args:
        role_id (str): Role identifier.
        protocol (dict): Governance protocol dict.

    Returns:
        Dict: Permissions dict for the role.
    """
    return protocol.get('role_permissions', {}).get(role_id, {})
