#!/usr/bin/env python3
"""
Markdown Wrapper Cleanup Agent
Removes markdown code block wrappers from generated Python files.
Reusable for any similar task.
"""

import ollama
from pathlib import Path

class MarkdownCleanupAgent:
    """Autonomous agent for removing markdown code block wrappers."""

    def __init__(self, root_path: Path):
        self.root = root_path
        self.fixed_files = []

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
        self.fixed_files.append(path.name)

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

    def clean_file(self, file_path: Path) -> bool:
        """Remove markdown wrappers from file."""
        if not file_path.exists():
            return False

        content = self.read_file(file_path)

        # Check if wrapped in markdown
        if not content.startswith("```"):
            return False

        # Detect the code block language (python, markdown, etc)
        lines = content.split('\n')
        first_line = lines[0]

        # Extract language hint
        lang = first_line.replace("```", "").strip()

        # Find content between markers
        start_idx = 1  # Skip opening marker
        end_idx = len(lines)

        # Find closing marker
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "```":
                end_idx = i
                break

        # Extract clean content
        clean_lines = lines[start_idx:end_idx]

        # Remove trailing empty lines
        while clean_lines and not clean_lines[-1].strip():
            clean_lines.pop()

        cleaned = '\n'.join(clean_lines)

        if cleaned.strip():
            self.write_file(file_path, cleaned)
            return True

        return False

    def scan_and_clean(self, target_dir: Path, pattern: str = "*.py") -> int:
        """Scan directory for markdown-wrapped files and clean them."""
        self.section(f"Scanning {target_dir.name}")

        count = 0
        for file_path in target_dir.glob(pattern):
            if file_path.is_file():
                if self.clean_file(file_path):
                    self.log(f"✓ Cleaned: {file_path.name}")
                    count += 1

        return count

    def run(self):
        """Execute cleanup across all relevant directories."""
        print("\n" + "="*70)
        print("  MARKDOWN CLEANUP AGENT")
        print("="*70)

        total_fixed = 0

        # Clean D:\ClaudeClockwork Python files
        cw_agents = Path("/mnt/d/ClaudeClockwork/claudeclockwork/agents")
        total_fixed += self.scan_and_clean(cw_agents, "*.py")

        cw_impl = Path("/mnt/d/ClaudeClockwork/claudeclockwork/agents/implementations")
        total_fixed += self.scan_and_clean(cw_impl, "*.py")

        # Print summary
        self.section("SUMMARY")

        if self.fixed_files:
            print(f"\n✓ Fixed {len(self.fixed_files)} file(s):")
            for f in self.fixed_files:
                print(f"  - {f}")
        else:
            print("\n✓ No markdown-wrapped files found")

        print("\n" + "="*70 + "\n")

        return len(self.fixed_files)


if __name__ == "__main__":
    import sys
    agent = MarkdownCleanupAgent(Path("/mnt/d/ClaudeClockwork"))
    count = agent.run()
    sys.exit(0 if count >= 0 else 1)
