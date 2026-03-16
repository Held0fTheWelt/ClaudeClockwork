#!/usr/bin/env python3
"""
Reporter archetype: Generates human-readable reports.

A reporter task formats data into readable reports with summaries, lists,
and metadata.

Main function signature:
  report(input_spec: Dict) -> Dict

Returns a dictionary with:
  - "report": str - formatted report text
  - metadata: additional fields as needed

Exit codes: 0 on success, 1 on failure.
"""

import json
import sys
from typing import Any, Dict


def report(input_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a human-readable report from input data.

    Args:
        input_spec: Dictionary containing data to report on

    Returns:
        Dictionary with at least:
        {
            "report": str,
            ...other metadata fields
        }

    Raises:
        NotImplementedError: This is a template stub
    """
    raise NotImplementedError("report() must be implemented")


def main() -> None:
    """Entry point for reporter archetype."""
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

        # Call the report function
        output = report(input_data)

        # Validate output is a dictionary with report field
        if not isinstance(output, dict):
            result = {
                "success": False,
                "error": "report() must return a dictionary"
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        if "report" not in output:
            result = {
                "success": False,
                "error": "report() must return a dictionary with 'report' field"
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        if not isinstance(output["report"], str):
            result = {
                "success": False,
                "error": "report field must be a string"
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        # Output result as JSON
        json.dump(output, sys.stdout)
        sys.exit(0)

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
            "error": f"Report generation failed: {str(e)}"
        }
        json.dump(result, sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
