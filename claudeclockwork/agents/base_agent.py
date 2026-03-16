"""Base agent framework for autonomous task execution."""

import ollama
from pathlib import Path
import subprocess
import json

class BaseAgent:
    """Base class for autonomous agents."""

    def __init__(self, project_root: Path = None):
        self.root = project_root or Path.cwd()
        self.modified_files = []
        self.results = {}

    def log(self, msg: str):
        print(f"    {msg}")

    def read_file(self, path: str) -> str:
        """Read file content."""
        full_path = self.root / path
        if not full_path.exists():
            return ""
        return full_path.read_text()

    def write_file(self, path: str, content: str) -> bool:
        """Write file content."""
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        self.modified_files.append(path)
        return True

    def run_ollama(self, prompt: str, model: str = "gemma3:latest") -> str:
        """Call Ollama with prompt."""
        try:
            response = ollama.generate(
                model=model,
                prompt=prompt,
                stream=False,
            )
            return response.get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)[:100]}]"

    def git_add(self, files: list = None) -> bool:
        """Stage files for commit."""
        files_to_add = files or self.modified_files
        if not files_to_add:
            return False
        try:
            subprocess.run(
                ["git", "add"] + files_to_add,
                cwd=str(self.root),
                capture_output=True,
                check=True,
            )
            return True
        except:
            return False

    def git_commit(self, message: str) -> bool:
        """Commit staged changes."""
        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.root),
                capture_output=True,
                check=True,
            )
            return True
        except:
            return False

    def report(self):
        """Print results summary."""
        print(f"\n{'─'*70}")
        print("  RESULTS")
        print(f"{'─'*70}")
        for key, val in self.results.items():
            print(f"  {key}: {val}")
        print(f"  Files modified: {len(self.modified_files)}")
