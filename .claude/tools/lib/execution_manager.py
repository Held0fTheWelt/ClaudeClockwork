import yaml
from typing import Dict, Tuple, List


def load_execution_framework(config_path: str) -> Dict:
    """
    Load execution framework from YAML file.

    Args:
        config_path (str): Path to execution_framework.yaml.

    Returns:
        Dict: Parsed execution framework.

    Raises:
        FileNotFoundError: If file not found.
        yaml.YAMLError: If YAML parse error.
    """
    try:
        with open(config_path) as f:
            data = yaml.safe_load(f)
            return data.get('execution_framework', {}) if isinstance(data, dict) else {}
    except FileNotFoundError:
        raise FileNotFoundError(f"Execution framework not found: {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing execution framework: {e}")


def validate_agents(framework: dict) -> Tuple[bool, List[str]]:
    """
    Validate all agents are properly defined.

    Args:
        framework (dict): Execution framework dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    required_fields = {'id', 'name', 'role', 'max_concurrent_tasks'}
    
    for agent_key, agent_data in framework.get('agents', {}).items():
        missing = required_fields - set(agent_data.keys())
        if missing:
            errors.append(f"Agent {agent_key} missing {missing}")
    
    return len(errors) == 0, errors


def validate_task_templates(framework: dict) -> Tuple[bool, List[str]]:
    """
    Validate all task templates are properly defined.

    Args:
        framework (dict): Execution framework dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    required_fields = {'id', 'name', 'steps'}
    
    for template_key, template_data in framework.get('task_templates', {}).items():
        missing = required_fields - set(template_data.keys())
        if missing:
            errors.append(f"Template {template_key} missing {missing}")
        
        if not template_data.get('steps'):
            errors.append(f"Template {template_key} has no steps")
    
    return len(errors) == 0, errors


def validate_workflows(framework: dict) -> Tuple[bool, List[str]]:
    """
    Validate all workflows are properly defined.

    Args:
        framework (dict): Execution framework dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    templates = set(framework.get('task_templates', {}).keys())
    
    for workflow_key, workflow_data in framework.get('workflow_definitions', {}).items():
        for step in workflow_data.get('steps', []):
            if step not in templates:
                errors.append(f"Workflow {workflow_key} references undefined template {step}")
    
    return len(errors) == 0, errors


def validate_quality_gates(framework: dict) -> Tuple[bool, List[str]]:
    """
    Validate all quality gates are properly defined.

    Args:
        framework (dict): Execution framework dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    
    for gate_key, gate_data in framework.get('quality_gates', {}).items():
        if 'threshold' not in gate_data or not (0 <= gate_data['threshold'] <= 100):
            errors.append(f"Quality gate {gate_key} has invalid threshold")
    
    return len(errors) == 0, errors


def validate_performance_budgets(framework: dict) -> Tuple[bool, List[str]]:
    """
    Validate all performance budgets are properly defined.

    Args:
        framework (dict): Execution framework dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    
    for budget_key, budget_data in framework.get('performance_budgets', {}).items():
        if budget_data.get('token_budget', 0) <= 0:
            errors.append(f"Budget {budget_key} has invalid token budget")
        if budget_data.get('time_budget_seconds', 0) <= 0:
            errors.append(f"Budget {budget_key} has invalid time budget")
    
    return len(errors) == 0, errors


def check_execution_consistency(framework: dict) -> Tuple[bool, List[str]]:
    """
    Check overall execution framework consistency.

    Args:
        framework (dict): Execution framework dict.

    Returns:
        Tuple[bool, List[str]]: (is_valid, errors).
    """
    errors = []
    
    # Validate components
    valid, errs = validate_agents(framework)
    if not valid:
        errors.extend(errs)
    
    valid, errs = validate_task_templates(framework)
    if not valid:
        errors.extend(errs)
    
    valid, errs = validate_workflows(framework)
    if not valid:
        errors.extend(errs)
    
    valid, errs = validate_quality_gates(framework)
    if not valid:
        errors.extend(errs)
    
    valid, errs = validate_performance_budgets(framework)
    if not valid:
        errors.extend(errs)
    
    return len(errors) == 0, errors
