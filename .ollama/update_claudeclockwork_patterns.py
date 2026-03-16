#!/usr/bin/env python3
"""
Update ClaudeClockwork BaseAgent with missing patterns.
Focused agent to add: section() method, logging setup, files_modified tracking.
"""

import ollama
from pathlib import Path

CW_ROOT = Path("/mnt/d/ClaudeClockwork")

class UpdateAgent:
    """Add missing patterns to ClaudeClockwork."""

    def __init__(self):
        self.changes = []

    def log(self, msg: str):
        print(f"  {msg}")

    def read_file(self, path: Path) -> str:
        return path.read_text() if path.exists() else ""

    def write_file(self, path: Path, content: str):
        path.write_text(content)
        self.changes.append(str(path.relative_to(CW_ROOT)))

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

    def update_base_agent(self):
        """Add missing methods to BaseAgent."""
        print("\n" + "─"*70)
        print("  Updating BaseAgent with missing patterns")
        print("─"*70 + "\n")

        base_file = CW_ROOT / "claudeclockwork/agents/base_agent.py"
        content = self.read_file(base_file)

        # Check what's missing
        needs_section = "def section(" not in content
        needs_files_tracking = "self.files_modified" not in content
        needs_logging = "import logging" not in content

        if not needs_section and not needs_logging and not needs_files_tracking:
            self.log("✓ BaseAgent already has all patterns")
            return True

        prompt = f"""Add missing patterns to ClaudeClockwork BaseAgent.__init__()

Current __init__ excerpt:
{chr(10).join(content.split(chr(10))[8:30])}

ADD to __init__:
1. Initialize: self.files_modified = [] (for tracking changes)
2. Add import logging at top (if missing)
3. Add self.logger = logging.getLogger(__name__)

ADD method (before read_file):
def section(self, title: str):
    '''Format section headers with separators.'''
    print(f"\\n{{'─'*70}}")
    print(f"  {{title}}")
    print(f"{{'─'*70}}")

Output ONLY the complete updated BaseAgent class code. Keep all existing methods.
Preserve all original functionality."""

        updated = self.run_ollama(prompt)

        if updated and "def section(" in updated and len(updated) > 500:
            self.write_file(base_file, updated)
            self.log("✓ Updated BaseAgent")
            return True
        else:
            self.log("⚠ Could not generate complete update")
            return False

    def update_orchestrator(self):
        """Ensure orchestrator uses new patterns."""
        print("\n" + "─"*70)
        print("  Checking orchestrator")
        print("─"*70 + "\n")

        orch_file = CW_ROOT / "claudeclockwork/agents/orchestrator.py"
        content = self.read_file(orch_file)

        if "self.files_modified" in content:
            self.log("✓ Orchestrator already tracks files")
            return True

        # Minimal update - add tracking
        if "def __init__" in content:
            lines = content.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                if "self.failed = []" in line:
                    new_lines.append("        self.files_modified = []")

            updated = '\n'.join(new_lines)
            self.write_file(orch_file, updated)
            self.log("✓ Added file tracking to orchestrator")
            return True

        return False

    def update_example_agent(self):
        """Update example agent to use section() pattern."""
        print("\n" + "─"*70)
        print("  Checking example agent")
        print("─"*70 + "\n")

        example_file = CW_ROOT / "claudeclockwork/agents/implementations/example.py"
        content = self.read_file(example_file)

        if "self.section(" in content or "print(f" not in content:
            self.log("✓ Example agent is current")
            return True

        # Add section usage
        if "class ExampleAgent" in content:
            updated = content.replace(
                'def execute(self, task):',
                'def execute(self, task):\n        self.section("Executing Task")'
            )
            self.write_file(example_file, updated)
            self.log("✓ Updated example to use section()")
            return True

        return False

    def run(self):
        """Execute updates."""
        print("\n" + "="*70)
        print("  CLAUDECLOCKWORK PATTERN UPDATE AGENT")
        print("="*70)

        r1 = self.update_base_agent()
        r2 = self.update_orchestrator()
        r3 = self.update_example_agent()

        print("\n" + "="*70)
        print("  SUMMARY")
        print("="*70)

        if self.changes:
            print(f"\n✓ Updated {len(self.changes)} file(s):")
            for f in self.changes:
                print(f"  - {f}")
        else:
            print("\n✓ All patterns already present")

        print("\n" + "="*70 + "\n")

        return all([r1, r2, r3])


if __name__ == "__main__":
    import sys
    agent = UpdateAgent()
    success = agent.run()
    sys.exit(0 if success else 1)
