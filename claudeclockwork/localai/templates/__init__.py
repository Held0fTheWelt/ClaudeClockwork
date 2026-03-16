"""
Archetype templates for skill-forge code generation.

Provides template code for the five constrained archetypes:
- Scanner: Collects and reports data
- Validator: Validates input, returns pass/fail with reasons
- Reporter: Generates human-readable reports
- Transformer: ETL - transforms input to output
- Registry Helper: Modifies/queries skill registry (YAML-safe only)
"""

import os
from typing import Dict


# Map of archetype names to their template files
ARCHETYPE_FILES: Dict[str, str] = {
    "scanner": "scanner.py",
    "validator": "validator.py",
    "reporter": "reporter.py",
    "transformer": "transformer.py",
    "registry_helper": "registry_helper.py",
}


def get_template(archetype: str) -> str:
    """
    Get the template code for a given archetype.

    Args:
        archetype: Name of archetype (scanner, validator, reporter, transformer, registry_helper)

    Returns:
        Template code as string

    Raises:
        ValueError: If archetype is not recognized
    """
    if archetype not in ARCHETYPE_FILES:
        raise ValueError(
            f"Unknown archetype: {archetype}. "
            f"Valid options: {', '.join(ARCHETYPE_FILES.keys())}"
        )

    template_file = ARCHETYPE_FILES[archetype]
    template_path = os.path.join(os.path.dirname(__file__), template_file)

    with open(template_path, "r") as f:
        return f.read()


__all__ = ["get_template", "ARCHETYPE_FILES"]
