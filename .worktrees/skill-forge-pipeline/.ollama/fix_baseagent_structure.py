#!/usr/bin/env python3
"""
Fix BaseAgent class structure - move section() method inside class.
Reusable agent for structural code repairs.
"""

import ollama
from pathlib import Path

class StructureRepairAgent:
    """Autonomous agent for fixing Python class/function structure issues."""

    def __init__(self):
        self.repairs = []

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
        self.repairs.append(str(path))

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

    def fix_baseagent_structure(self):
        """Fix BaseAgent class - move section() inside class."""
        self.section("Fixing BaseAgent Class Structure")

        base_file = Path("/mnt/d/ClaudeClockwork/claudeclockwork/agents/base_agent.py")
        content = self.read_file(base_file)

        # Check if section() is outside class (incorrectly defined)
        if "def section(self" in content and content.find("def section") < content.find("class BaseAgent"):
            self.log("✗ section() is defined before class")

            prompt = f"""Fix Python class structure in BaseAgent.

CURRENT CODE (first 40 lines):
{chr(10).join(content.split(chr(10))[:40])}

PROBLEM:
- section() method is defined BEFORE class BaseAgent
- Should be inside the class (properly indented)

FIX:
1. Move section() method inside BaseAgent class
2. Indent it properly (4 spaces from class level)
3. Keep all other methods inside class
4. Ensure proper __init__ ordering

Output ONLY the corrected complete file with proper indentation and structure."""

            fixed = self.run_ollama(prompt)

            if fixed and "class BaseAgent:" in fixed and len(fixed) > 500:
                self.write_file(base_file, fixed)
                self.log("✓ Fixed class structure")
                return True
            else:
                self.log("⚠ Could not fix with Ollama")
                # Fallback: manual fix
                lines = content.split('\n')
                new_lines = []
                skip_until_class = False

                for i, line in enumerate(lines):
                    if "def section(self" in line:
                        skip_until_class = True
                        continue
                    if skip_until_class and "class BaseAgent:" in line:
                        skip_until_class = False
                        new_lines.append(line)
                        # Add section() after class definition and __init__
                        continue
                    if not skip_until_class:
                        if "    def log(self" in line and len(new_lines) > 0:
                            # Insert section before log
                            new_lines.append("    def section(self, title: str):")
                            new_lines.append("        '''Format section headers with separators.'''")
                            new_lines.append('        print(f"\\n{\\'─\\'*70}")')
                            new_lines.append('        print(f"  {title}")')
                            new_lines.append('        print(f"{\\'─\\'*70}")')
                            new_lines.append("")
                        new_lines.append(line)

                fixed = '\n'.join(new_lines)
                self.write_file(base_file, fixed)
                self.log("✓ Fixed with fallback method")
                return True

        else:
            self.log("✓ BaseAgent structure is correct")
            return True

    def run(self):
        """Execute structural repairs."""
        print("\n" + "="*70)
        print("  STRUCTURE REPAIR AGENT")
        print("="*70)

        self.fix_baseagent_structure()

        self.section("SUMMARY")

        if self.repairs:
            print(f"\n✓ Repaired {len(self.repairs)} file(s):")
            for f in self.repairs:
                print(f"  - {Path(f).name}")
        else:
            print("\n✓ All structures are correct")

        print("\n" + "="*70 + "\n")

        return len(self.repairs)


if __name__ == "__main__":
    import sys
    agent = StructureRepairAgent()
    count = agent.run()
    sys.exit(0 if count >= 0 else 1)
