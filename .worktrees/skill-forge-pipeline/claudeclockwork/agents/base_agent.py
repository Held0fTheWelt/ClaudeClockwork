import os
import subprocess
from pathlib import Path

class BaseAgent:
    def __init__(self, root: Path):
        self.root = root

    def section(self, title: str):
        '''Format section headers with separators.'''
        print(f"\n{'-'*70}")
        print(f"  {title}")
        print(f"{'-'*70}")

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

    def run_ollama(self, prompt: str, model: str = "gemma3:latest") -> str:
        """Calls ollama.generate() with given prompt and returns response content."""
        try:
            result = subprocess.run(
                ["ollama", "generate", prompt, "-m", model],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except FileNotFoundError:
            self.log("Error: ollama command not found.  Make sure ollama is installed and in your PATH.")
            return ""
        except subprocess.CalledProcessError as e:
            self.log(f"Error running ollama: {e}")
            self.log(f"Stderr: {e.stderr}")
            return ""
        except Exception as e:
            self.log(f"An unexpected error occurred: {e}")
            return ""

    def git_add(self, files: list = None) -> bool:
        """Stages files for commit using subprocess.run(["git", "add", ...])."""
        try:
            if files is None:
                files = ["."]  # Default to adding current directory if no files are specified
            cmd = ["git", "add"] + files
            result = subprocess.run(cmd, cwd=self.root, check=True, capture_output=True, text=True)
            self.log(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Error running git add: {e}")
            self.log(f"Stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            self.log("Error: git command not found. Make sure git is installed and in your PATH.")
            return False
        except Exception as e:
            self.log(f"An unexpected error occurred: {e}")
            return False

    def git_commit(self, message: str) -> bool:
        """Commits staged changes with subprocess.run(["git", "commit", "-m", message])."""
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True
            )
            self.log(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Error running git commit: {e}")
            self.log(f"Stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            self.log("Error: git command not found. Make sure git is installed and in your PATH.")
            return False
        except Exception as e:
            self.log(f"An unexpected error occurred: {e}")
            return False