import yaml
from pathlib import Path
from typing import Dict, Tuple


def load_runtime_config(config_path: str) -> Dict:
    """
    Load local_ollama_runtime.yaml as canonical SSOT for runtime config.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: Loaded configuration dictionary.

    Raises:
        FileNotFoundError: If the specified config file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML: {e}")


def validate_model_availability(model_name: str, config: Dict) -> Tuple[bool, str]:
    """
    Check if the model exists in the available models list.

    Args:
        model_name (str): The name of the model to check.
        config (dict): The loaded configuration dictionary.

    Returns:
        tuple: A tuple containing a boolean indicating availability and an error message if unavailable.
    """
    available_models = config.get('models', {}).keys()
    if model_name in available_models:
        return True, ''
    else:
        return False, f"Model '{model_name}' is not available."


def validate_model_tier(model_name: str, config: Dict) -> Tuple[bool, str]:
    """
    Check if the model tier is allowed based on hardware constraints.

    Args:
        model_name (str): The name of the model to check.
        config (dict): The loaded configuration dictionary.

    Returns:
        tuple: A tuple containing a boolean indicating if the model tier is allowed and an error message if not allowed.

    Note:
        Forbidden escalations: 32B/70B/72B models on GPU (CPU-only for large models).
    """
    hardware_constraints = config.get('constraints', {})
    model_info = config.get('models', {}).get(model_name, {})

    # Example model tier to size mapping
    tier_to_size = {'32B': 'large', '70B': 'larger', '72B': 'largest'}
    
    if hardware_constraints.get('hardware') == 'GPU':
        for size in ['large', 'larger', 'largest']:
            if model_info.get('tier') == tier_to_size[size]:
                return False, f"Model '{model_name}' of tier {model_info['tier']} is not allowed on GPU."

    return True, ''


def get_model_timeouts(model_name: str, config: Dict) -> Dict[str, int]:
    """
    Return timeout settings for the specified model.

    Args:
        model_name (str): The name of the model to retrieve timeouts for.
        config (dict): The loaded configuration dictionary.

    Returns:
        dict: Timeout settings including connect_timeout, health_timeout,
              request_timeout, and agent_step_timeout.
    """
    model_config = config.get('models', {}).get(model_name, {})
    return {
        'connect_timeout': model_config.get('connect_timeout', 0),
        'health_timeout': model_config.get('health_timeout', 0),
        'request_timeout': model_config.get('request_timeout', 0),
        'agent_step_timeout': model_config.get('agent_step_timeout', 0)
    }


def get_model_constraints(model_name: str, config: Dict) -> Dict[str, int]:
    """
    Return model constraints for the specified model.

    Args:
        model_name (str): The name of the model to retrieve constraints for.
        config (dict): The loaded configuration dictionary.

    Returns:
        dict: Model constraints including num_parallel, max_loaded_models,
              and memory_limit.
    """
    model_config = config.get('models', {}).get(model_name, {})
    return {
        'num_parallel': model_config.get('num_parallel', 0),
        'max_loaded_models': model_config.get('max_loaded_models', 0),
        'memory_limit': model_config.get('memory_limit', 0)
    }
