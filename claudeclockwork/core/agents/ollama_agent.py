"""Ollama-based autonomous agent for task execution and code generation.

Pure local inference - no Claude API dependency. Agent uses Ollama for reasoning,
generates Python code to accomplish tasks, executes code, learns from results.

Model resolution (precedence): per-invocation override > profile-configured model > global default.
Context: bounded by profile/model prompt_budget_chars; oversized payloads truncated safely.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from claudeclockwork.core.mode import ModeManager
from claudeclockwork.core.ollama import OllamaModelManager, apply_budget


class OllamaAgent:
    """Self-improving Ollama agent that reasons locally and generates executable code."""

    def __init__(
        self,
        model: str | None = None,
        mode: str = "default",
        profile: str | None = None,
        project_root: str | Path | None = None,
    ):
        """
        Initialize Ollama agent.

        Args:
            model: Per-invocation override. If set, used as-is (does not mutate state).
            mode: Mode to enforce (default, adaptive, claude-min).
            profile: Agent profile name for model/budget (e.g. implementation, architecture, review).
                     Resolution: model override > profile model > global default.
            project_root: Project root for config/state (default: cwd).
        """
        root = Path(project_root).resolve() if project_root else Path.cwd()
        manager = OllamaModelManager(project_root=root)
        resolved, source = manager.resolve_model(override=model, profile=profile)
        self.model = resolved
        self._model_source = source  # 'override' | 'profile' | 'global'
        self._profile = profile
        self._project_root = root
        self._manager = manager
        self.mode_manager = ModeManager()
        self.mode_manager.set_mode(mode)
        self.conversation_history = []
        self.generated_code = []
        self.execution_results = []
        self._ollama_available = self._check_ollama_available()

    @staticmethod
    def _check_ollama_available() -> bool:
        """Check if Ollama is available and running."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                timeout=2,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def reason(self, prompt: str, context: str = "", verbose: bool = False) -> str:
        """
        Use Ollama to reason about a task locally. Context is bounded by profile/global
        prompt_budget_chars; oversized payloads are truncated (tail) before dispatch.
        """
        if not self._ollama_available:
            error_msg = "Ollama not available. Install Ollama and run 'ollama serve' in another terminal."
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            if verbose:
                print(f"[OllamaAgent] ❌ {error_msg}", file=sys.stderr)
            return error_msg

        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        budget = self._manager.get_prompt_budget(profile=self._profile)
        bounded_prompt = apply_budget(full_prompt, budget, strategy="truncate_tail")

        self.conversation_history.append({"role": "user", "content": full_prompt})

        if verbose:
            print(f"[OllamaAgent] 🧠 Reasoning with {self.model}...", file=sys.stderr)

        try:
            if verbose:
                result = subprocess.run(
                    ["ollama", "run", self.model],
                    input=bounded_prompt,
                    capture_output=True,
                    text=True,
                    timeout=1800,
                )
            else:
                result = subprocess.run(
                    ["ollama", "run", "--nowordwrap", self.model],
                    input=bounded_prompt,
                    capture_output=True,
                    text=True,
                    timeout=1800,
                )

            reasoning = result.stdout.strip() if result.returncode == 0 else result.stderr
            reasoning = self._strip_ansi_codes(reasoning)
            self.conversation_history.append({"role": "assistant", "content": reasoning})

            if verbose:
                print(f"[OllamaAgent] ✓ Reasoning complete ({len(reasoning)} chars)", file=sys.stderr)

            return reasoning

        except subprocess.TimeoutExpired:
            error_msg = "Ollama reasoning timeout (10min) - model may be slow or not loaded"
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            if verbose:
                print(f"[OllamaAgent] ⏱️  {error_msg}", file=sys.stderr)
            return error_msg

        except Exception as e:
            error_msg = f"Ollama reasoning failed: {str(e)}"
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            if verbose:
                print(f"[OllamaAgent] ❌ {error_msg}", file=sys.stderr)
            return error_msg

    def generate_code(self, task: str, language: str = "python") -> str:
        """Generate code to accomplish a task using Ollama reasoning."""
        code_prompt = f"""
You are a code generation expert. Generate {language} code to accomplish this task:

{task}

Requirements:
- Code must be complete and runnable
- Include error handling
- Add comments explaining key sections
- Use modern best practices for {language}
- If using Python, import all needed modules
- Output ONLY the code, no explanation

Task: {task}
"""
        reasoning = self.reason(code_prompt)
        code = self._extract_code(reasoning, language)
        if not code:
            code = reasoning
        self.generated_code.append({"task": task, "language": language, "code": code})
        return code

    def execute_code(self, code: str, language: str = "python") -> dict[str, Any]:
        """Execute generated code locally."""
        try:
            if language == "python":
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            elif language == "bash":
                result = subprocess.run(
                    code,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            else:
                return {
                    "success": False,
                    "language": language,
                    "error": f"Unsupported language: {language}",
                }
            execution_result = {
                "success": result.returncode == 0,
                "language": language,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            self.execution_results.append(execution_result)
            return execution_result
        except subprocess.TimeoutExpired:
            timeout_result = {
                "success": False,
                "language": language,
                "error": "Execution timeout (30s)",
            }
            self.execution_results.append(timeout_result)
            return timeout_result
        except Exception as e:
            return {
                "success": False,
                "language": language,
                "error": str(e),
            }

    def execute_task(self, task: str, max_iterations: int = 3, verbose: bool = False) -> dict[str, Any]:
        """Execute a task: reason → generate code → execute → iterate on errors."""
        iteration = 0
        current_code = None
        last_error = None

        if verbose:
            print(f"[OllamaAgent] 🚀 Starting task execution (max {max_iterations} iterations)", file=sys.stderr)

        while iteration < max_iterations:
            iteration += 1
            if verbose:
                print(f"[OllamaAgent] Iteration {iteration}/{max_iterations}...", file=sys.stderr)
            error_context = (
                f"Previous attempt failed with error:\n{last_error}\n\nGenerate corrected code:"
                if last_error
                else ""
            )
            if verbose:
                print(f"[OllamaAgent]   📝 Generating code...", file=sys.stderr)
            current_code = self.generate_code(task, language="python")
            if verbose:
                print(f"[OllamaAgent]   ⚙️  Executing code...", file=sys.stderr)
            result = self.execute_code(current_code, language="python")
            if result["success"]:
                if verbose:
                    print(f"[OllamaAgent] ✅ Task completed in {iteration} iteration(s)", file=sys.stderr)
                return {
                    "success": True,
                    "task": task,
                    "iterations": iteration,
                    "code": current_code,
                    "output": result["stdout"],
                    "mode": self.mode_manager.get_active_mode(),
                }
            last_error = result.get("stderr") or result.get("error", "Unknown error")
            if verbose:
                print(f"[OllamaAgent]   ⚠️  Iteration failed: {last_error[:100]}...", file=sys.stderr)

        if verbose:
            print(f"[OllamaAgent] ❌ Task failed after {iteration} iterations", file=sys.stderr)
        return {
            "success": False,
            "task": task,
            "iterations": iteration,
            "code": current_code,
            "error": last_error,
            "mode": self.mode_manager.get_active_mode(),
        }

    def generate_script(self, task: str, output_file: str | Path | None = None) -> str:
        """Generate a standalone Python script to accomplish a task."""
        code = self.generate_code(task, language="python")
        script = f'''#!/usr/bin/env python3
"""Auto-generated script for task execution.

Task: {task}
Generated by OllamaAgent using local Ollama inference.
"""
from __future__ import annotations

import sys

def main():
    """Execute task."""
{self._indent_code(code, 4)}

if __name__ == "__main__":
    sys.exit(main())
'''
        if output_file:
            Path(output_file).write_text(script)
            Path(output_file).chmod(0o755)
        return script

    def get_summary(self) -> dict[str, Any]:
        """Get summary of agent's work so far."""
        return {
            "model": self.model,
            "mode": self.mode_manager.get_active_mode(),
            "reasoning_turns": len(self.conversation_history) // 2,
            "code_generated": len(self.generated_code),
            "code_executed": len(self.execution_results),
            "successful_executions": sum(
                1 for r in self.execution_results if r.get("success")
            ),
        }

    @staticmethod
    def _extract_code(reasoning: str, language: str) -> str:
        """Extract code from reasoning output (look for code block markers)."""
        import re
        patterns = [
            f"```{language}\n(.*?)\n```",
            f"```\n(.*?)\n```",
            "```(.*?)```",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, reasoning, re.DOTALL)
            if matches:
                return matches[0].strip()
        return ""

    @staticmethod
    def _indent_code(code: str, spaces: int) -> str:
        """Indent code by N spaces."""
        indent = " " * spaces
        return "\n".join(f"{indent}{line}" if line else "" for line in code.split("\n"))

    @staticmethod
    def _strip_ansi_codes(text: str) -> str:
        """Remove ANSI escape codes from text."""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


def main() -> int:
    """CLI entry point. Uses managed active model unless --model is set."""
    import argparse

    parser = argparse.ArgumentParser(description="Ollama-based task executor")
    parser.add_argument("task", help="Task description")
    parser.add_argument(
        "--model",
        default=None,
        help="Ollama model (default: use active model from ollama_model_manage state)",
    )
    parser.add_argument("--mode", default="default", help="Mode to enforce")
    parser.add_argument("--profile", default=None, help="Agent profile for model/budget (e.g. implementation, review)")
    parser.add_argument("--script", help="Save generated script to file instead of executing")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--project-root", type=Path, default=None, help="Project root for config/state")

    args = parser.parse_args()

    agent = OllamaAgent(
        model=args.model or None,
        mode=args.mode,
        profile=args.profile or None,
        project_root=args.project_root,
    )

    if args.verbose:
        print(f"[Ollama Agent] Mode: {args.mode}", file=sys.stderr)
        print(f"[Ollama Agent] Model: {agent.model}", file=sys.stderr)

    if args.script:
        script = agent.generate_script(args.task, output_file=args.script)
        if args.verbose:
            print(f"[Ollama Agent] Script saved to {args.script}", file=sys.stderr)
        print(script)
        return 0

    result = agent.execute_task(args.task, verbose=args.verbose)
    if args.verbose:
        print(f"[Ollama Agent] Summary: {json.dumps(agent.get_summary(), indent=2)}", file=sys.stderr)
    print(json.dumps(result, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
