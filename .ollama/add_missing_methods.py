#!/usr/bin/env python3
"""
Add Missing Methods Agent
Adds run_ollama(), git_add(), and git_commit() to ClaudeClockwork BaseAgent.
"""

import ollama
from pathlib import Path

CW_ROOT = Path("/mnt/d/ClaudeClockwork")

class AddMethodsAgent:
    """Autonomous agent to add missing methods to BaseAgent."""

    def __init__(self):
        self.changes = []

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def read_file(self, path: Path) -> str:
        return path.read_text() if path.exists() else ""

    def write_file(self, path: Path, content: str):
        path.write_text(content)
        self.changes.append(path.name)

    def run_ollama(self, prompt: str) -> str:
        try:
            response = ollama.generate(
                model="gemma3:latest",
                prompt=prompt,
                stream=False,
            )
            return response.get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)[:100]}]"

    def add_missing_methods(self):
        """Add run_ollama, git_add, git_commit to BaseAgent."""
        self.section("Adding Missing Methods")

        base_file = CW_ROOT / "claudeclockwork/agents/base_agent.py"
        content = self.read_file(base_file)

        # Check what's missing
        needs_run_ollama = "def run_ollama(" not in content
        needs_git_add = "def git_add(" not in content
        needs_git_commit = "def git_commit(" not in content

        if not (needs_run_ollama or needs_git_add or needs_git_commit):
            self.log("✓ All methods already present")
            return True

        prompt = f"""Add three critical methods to BaseAgent class.

CURRENT BaseAgent (excerpt):
{chr(10).join(content.split(chr(10))[14:50])}

ADD these three methods to the class (before report() if it exists):

1. run_ollama(self, prompt: str, model: str = "gemma3:latest") -> str:
   - Calls ollama.generate() with given prompt
   - Returns response content
   - Handles exceptions gracefully

2. git_add(self, files: list = None) -> bool:
   - Stages files for commit using subprocess.run([\"git\", \"add\", ...])
   - Uses self.root as cwd
   - Returns success boolean

3. git_commit(self, message: str) -> bool:
   - Commits staged changes with subprocess.run([\"git\", \"commit\", \"-m\", message])
   - Uses self.root as cwd
   - Returns success boolean

Output ONLY the complete corrected BaseAgent class with all methods properly indented.
Include proper docstrings and error handling."""

        updated = self.run_ollama(prompt)

        if updated and "def run_ollama(" in updated and "def git_add(" in updated and len(updated) > 800:
            self.write_file(base_file, updated)
            self.log("✓ Added missing methods")
            return True
        else:
            self.log("⚠ Ollama generation incomplete, using fallback")
            # Fallback: append methods manually
            if "def report(" in content:
                insert_pos = content.rfind("def report(")
            else:
                insert_pos = len(content) - 100

            methods = '''
    def run_ollama(self, prompt: str, model: str = "gemma3:latest") -> str:
        """Call Ollama for content generation."""
        try:
            import ollama
            response = ollama.generate(model=model, prompt=prompt, stream=False)
            return response.get("response", "").strip()
        except Exception as e:
            self.log(f"Error calling Ollama: {str(e)[:50]}")
            return ""

    def git_add(self, files: list = None) -> bool:
        """Stage files for commit."""
        import subprocess
        files_to_add = files or self.files_modified
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
        except Exception:
            return False

    def git_commit(self, message: str) -> bool:
        """Commit staged changes."""
        import subprocess
        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.root),
                capture_output=True,
                check=True,
            )
            return True
        except Exception:
            return False
'''
            # Find last method in class
            lines = content.split('\n')
            last_method_line = -1
            for i in range(len(lines)-1, -1, -1):
                if lines[i].startswith("    def "):
                    last_method_line = i
                    break

            if last_method_line >= 0:
                # Find end of last method
                end_line = last_method_line + 1
                for i in range(last_method_line + 1, len(lines)):
                    if lines[i] and not lines[i].startswith("        "):
                        if lines[i].startswith("    def ") or lines[i].startswith("class "):
                            end_line = i
                            break
                    end_line = i

                lines.insert(end_line, methods)
                updated_content = '\n'.join(lines)
                self.write_file(base_file, updated_content)
                self.log("✓ Added methods with fallback")
                return True

        return False

    def run(self):
        """Execute method addition."""
        print("\n" + "="*70)
        print("  ADD MISSING METHODS AGENT")
        print("="*70)

        success = self.add_missing_methods()

        self.section("SUMMARY")

        if self.changes:
            print(f"\n✓ Updated {len(self.changes)} file(s):")
            for f in self.changes:
                print(f"  - {f}")
        else:
            print("\n✓ No changes needed")

        print("\n" + "="*70 + "\n")

        return success


if __name__ == "__main__":
    import sys
    agent = AddMethodsAgent()
    success = agent.run()
    sys.exit(0 if success else 1)
