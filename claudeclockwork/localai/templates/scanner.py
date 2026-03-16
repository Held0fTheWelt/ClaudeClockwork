#!/usr/bin/env python3
"""
Scanner archetype: Collects and reports data.

A scanner task gathers information from the system and returns structured data.
Examples: file discovery, metadata collection, log analysis.

Main function signature:
  scan(input_spec: Dict) -> Dict

Returns a dictionary with collected data.
Exit codes: 0 on success, 1 on failure.
"""

import json
import sys
from typing import Any, Dict


def scan(input_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scan and collect data based on input specification.

    Args:
        input_spec: Dictionary containing scan parameters

    Returns:
        Dictionary with collected data and metadata

    Raises:
        NotImplementedError: This is a template stub
    """
    raise NotImplementedError("scan() must be implemented")


def main() -> None:
    """Entry point for scanner archetype."""
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

        # Call the scan function
        output = scan(input_data)

        # Ensure output is a dictionary
        if not isinstance(output, dict):
            result = {
                "success": False,
                "error": "scan() must return a dictionary"
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
            "error": f"Scanner failed: {str(e)}"
        }
        json.dump(result, sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
