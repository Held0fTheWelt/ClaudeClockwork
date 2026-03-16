#!/usr/bin/env python3
"""
Validator archetype: Validates input and returns pass/fail with reasons.

A validator task checks if input meets required criteria and returns validation
results including error details.

Main function signature:
  validate(input_spec: Dict) -> Dict

Returns a dictionary with:
  - "valid": bool - whether input is valid
  - "errors": [str] - list of validation error messages

Exit codes: 0 if valid, 1 if invalid.
"""

import json
import sys
from typing import Any, Dict, List


def validate(input_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input specification.

    Args:
        input_spec: Dictionary to validate

    Returns:
        Dictionary with format:
        {
            "valid": bool,
            "errors": [str]
        }

    Raises:
        NotImplementedError: This is a template stub
    """
    raise NotImplementedError("validate() must be implemented")


def main() -> None:
    """Entry point for validator archetype."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Validate input_spec is a dictionary
        if not isinstance(input_data, dict):
            result = {
                "valid": False,
                "errors": ["input must be a JSON object"]
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        # Call the validate function
        output = validate(input_data)

        # Validate output format
        if not isinstance(output, dict):
            result = {
                "valid": False,
                "errors": ["validate() must return a dictionary"]
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        if "valid" not in output or "errors" not in output:
            result = {
                "valid": False,
                "errors": ["validate() must return {valid: bool, errors: [str]}"]
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        if not isinstance(output["valid"], bool):
            result = {
                "valid": False,
                "errors": ["valid field must be a boolean"]
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        if not isinstance(output["errors"], list):
            result = {
                "valid": False,
                "errors": ["errors field must be a list"]
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        # Output result as JSON
        json.dump(output, sys.stdout)

        # Exit with appropriate code
        sys.exit(0 if output["valid"] else 1)

    except json.JSONDecodeError as e:
        result = {
            "valid": False,
            "errors": [f"Invalid JSON input: {str(e)}"]
        }
        json.dump(result, sys.stdout)
        sys.exit(1)
    except Exception as e:
        result = {
            "valid": False,
            "errors": [f"Validation failed: {str(e)}"]
        }
        json.dump(result, sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
