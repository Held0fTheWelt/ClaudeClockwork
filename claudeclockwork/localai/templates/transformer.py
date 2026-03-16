#!/usr/bin/env python3
"""
Transformer archetype: ETL - transforms input to output.

A transformer task converts or migrates data from one format/structure to
another, with metadata about the transformation.

Main function signature:
  transform(input_spec: Dict) -> Dict

Returns a dictionary with:
  - "output": any - transformed data
  - metadata: additional fields as needed

Exit codes: 0 on success, 1 on failure.
"""

import json
import sys
from typing import Any, Dict


def transform(input_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform input data to output format.

    Args:
        input_spec: Dictionary containing data to transform

    Returns:
        Dictionary with at least:
        {
            "output": <transformed data>,
            ...other metadata fields
        }

    Raises:
        NotImplementedError: This is a template stub
    """
    raise NotImplementedError("transform() must be implemented")


def main() -> None:
    """Entry point for transformer archetype."""
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

        # Call the transform function
        output = transform(input_data)

        # Validate output is a dictionary with output field
        if not isinstance(output, dict):
            result = {
                "success": False,
                "error": "transform() must return a dictionary"
            }
            json.dump(result, sys.stdout)
            sys.exit(1)

        if "output" not in output:
            result = {
                "success": False,
                "error": "transform() must return a dictionary with 'output' field"
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
            "error": f"Transformation failed: {str(e)}"
        }
        json.dump(result, sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
