#!/usr/bin/env python3
"""
Generic Forge Pipeline Agent

A reusable Ollama agent launcher that executes ANY task through the skill-forge pipeline.
Works with any archetype, any task, any future use case without modification.

Usage:
    python generic_forge_agent.py <task_description>

Input: Task description (JSON or plain text describing what needs to be generated)
Output: Generated code/artifacts ready to use

This agent:
1. Parses the task description
2. Routes through the forge pipeline (plan → forge → review → validate)
3. Returns structured results
4. Can be called by any Ollama model for ANY future task
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

from claudeclockwork.localai.forge_runner import SkillForgeRunner


class GenericForgeAgent:
    """
    Reusable agent for executing ANY task through the skill-forge pipeline.

    Works with any:
    - Archetype (scanner, validator, reporter, transformer, registry_helper)
    - Task type (documentation, code, configuration)
    - Input format (JSON or natural language)
    """

    def __init__(self):
        self.runner = SkillForgeRunner()
        self.task_id = f"forge_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    def run(self, task_input: str) -> Dict[str, Any]:
        """
        Execute a task through the forge pipeline.

        Args:
            task_input: Task description (JSON or plain text)

        Returns:
            Structured result with success status and artifacts
        """

        # Parse task input
        forge_request = self._parse_input(task_input)

        if not forge_request:
            return {
                "success": False,
                "error": "Could not parse task input. Provide JSON with: archetype, purpose, constraints"
            }

        # Execute pipeline
        result = self.runner.run_pipeline(forge_request)

        # Return structured result
        return {
            "success": result.get("success", False),
            "task_id": forge_request.get("task_id", self.task_id),
            "archetype": forge_request.get("archetype"),
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _parse_input(self, task_input: str) -> Dict[str, Any]:
        """Parse task input (JSON or natural language)."""

        try:
            parsed = json.loads(task_input)
            return self._validate_request(parsed)
        except json.JSONDecodeError:
            return self._parse_natural_language(task_input)

    def _parse_natural_language(self, task_input: str) -> Dict[str, Any]:
        """Parse natural language task descriptions."""

        task_lower = task_input.lower()

        # Detect archetype from keywords
        archetype = self._detect_archetype(task_lower)
        if not archetype:
            return None

        purpose = task_input[:200]

        # Default constraints: safe defaults
        constraints = {
            "allowed_write_roots": [],  # Read-only by default
            "forbidden_patterns": ["shell=True", "eval", "exec"],
            "example_input": {},
            "example_output": {}
        }

        return {
            "task_id": self.task_id,
            "archetype": archetype,
            "purpose": purpose,
            "constraints": constraints,
            "input_schema": {"type": "object"},
            "output_schema": {"type": "object"}
        }

    def _detect_archetype(self, task_text: str) -> str:
        """Detect archetype from task keywords."""

        patterns = {
            "scanner": ["scan", "find", "collect", "gather", "list", "search"],
            "validator": ["validate", "check", "verify", "ensure", "confirm"],
            "reporter": ["report", "summarize", "analyze", "digest"],
            "transformer": ["transform", "convert", "migrate", "reformat"],
            "registry_helper": ["registry", "register"]
        }

        for archetype, keywords in patterns.items():
            if any(keyword in task_text for keyword in keywords):
                return archetype

        return None

    def _validate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate forge_request structure."""

        required = ["archetype", "purpose", "constraints"]
        if not all(key in request for key in required):
            return None

        valid_archetypes = ["scanner", "validator", "reporter", "transformer", "registry_helper"]
        if request.get("archetype") not in valid_archetypes:
            return None

        if "task_id" not in request:
            request["task_id"] = self.task_id

        if "input_schema" not in request:
            request["input_schema"] = {"type": "object"}
        if "output_schema" not in request:
            request["output_schema"] = {"type": "object"}

        return request


def main():
    """CLI entry point."""

    parser = argparse.ArgumentParser(
        description="Generic Forge Pipeline Agent - Execute ANY task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Use with any archetype (scanner, validator, reporter, transformer, registry_helper)"
    )

    parser.add_argument("task", help="Task description (JSON or natural language)")
    parser.add_argument("--output", help="Output file for results", default=None)

    args = parser.parse_args()

    agent = GenericForgeAgent()
    result = agent.run(args.task)

    output_json = json.dumps(result, indent=2)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Results written to: {args.output}")
    else:
        print(output_json)

    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
