#!/usr/bin/env python3
"""
Registry Helper archetype: Modifies/queries skill registry (YAML-safe only).

A registry helper performs safe read/write operations on the skill registry.
CRITICAL: Only reads/writes YAML files in allowed_write_roots. Never executes
arbitrary code from registry.

Main function signature:
  registry_op(input_spec: Dict) -> Dict

Returns a dictionary with:
  - "success": bool - operation succeeded
  - "error": str (optional) - error message if failed
  - result fields as needed

Exit codes: 0 on success, 1 on failure.
"""

import json
import sys
from typing import Any, Dict, Optional


def registry_op(input_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a safe registry operation (read or write).

    Args:
        input_spec: Dictionary specifying the operation

    Returns:
        Dictionary with format:
        {
            "success": bool,
            "error": str (optional),
            ...other result fields
        }

    Raises:
        NotImplementedError: This is a template stub
    """
    raise NotImplementedError("registry_op() must be implemented")


def main() -> None:
    """Entry point for registry helper archetype."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Validate input_spec is a dictionary
        if not isinstance(input_data, dict):
            result = {
                "success": False,
                "error": "input must be a JSON object"
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        # Call the registry_op function
        output = registry_op(input_data)

        # Validate output format
        if not isinstance(output, dict):
            result = {
                "success": False,
                "error": "registry_op() must return a dictionary"
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        if "success" not in output:
            result = {
                "success": False,
                "error": "registry_op() must return a dictionary with 'success' field"
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        if not isinstance(output["success"], bool):
            result = {
                "success": False,
                "error": "success field must be a boolean"
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        # Output result as JSON
        json.dump(output, sys.stdout)

        # Exit with appropriate code
        sys.exit(0 if output["success"] else 1)

    except json.JSONDecodeError as e:
        result = {
            "success": False,
            "error": f"Invalid JSON input: {str(e)}"
        }
        json.dump(result, sys.stdout)
        sys.exit(1)
    except Exception as e:
        result = {
            "success": False,
            "error": f"Registry operation failed: {str(e)}"
        }
        json.dump(result, sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
