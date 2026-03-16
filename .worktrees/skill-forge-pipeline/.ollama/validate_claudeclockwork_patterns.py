#!/usr/bin/env python3
"""
ClaudeClockwork Pattern Validation Agent
Validates that ClaudeClockwork matches WorldOfShadows autonomous agent patterns.
"""

import ollama
import subprocess
from pathlib import Path

WOS_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
CW_ROOT = Path("/mnt/d/ClaudeClockwork")

class PatternValidationAgent:
    """Ollama-powered validation agent for ClaudeClockwork patterns."""

    def __init__(self):
        self.findings = {}
        self.issues = []

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def read_file(self, path: Path) -> str:
        """Read file content."""
        return path.read_text() if path.exists() else ""

    def run_ollama(self, prompt: str) -> str:
        """Call Ollama for analysis."""
        try:
            response = ollama.generate(
                model="gemma3:latest",
                prompt=prompt,
                stream=False,
            )
            return response.get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)[:100]}]"

    def analyze_wos_patterns(self):
        """Analyze autonomous agent patterns in WorldOfShadows."""
        self.section("Analyzing WorldOfShadows Patterns")

        # Collect agent files
        agents_in_wos = list((WOS_ROOT / ".ollama").glob("*.py"))
        self.log(f"Found {len(agents_in_wos)} agent scripts in WorldOfShadows")

        # Read key agent files
        corrective_agent = self.read_file(WOS_ROOT / ".ollama/master_corrective_agent_v3.py")
        base_agent = self.read_file(WOS_ROOT / "claudeclockwork/agents/base_agent.py")

        prompt = f"""Analyze the autonomous agent patterns in WorldOfShadows codebase.

KEY FILES FOUND:
- {len(agents_in_wos)} agent scripts in .ollama/
- Base agent framework: claudeclockwork/agents/base_agent.py
- Orchestrator: claudeclockwork/agents/orchestrator.py

CORRECTIVE AGENT V3 (master_corrective_agent_v3.py) - SAMPLE (first 50 lines):
{chr(10).join(corrective_agent.split(chr(10))[:50])}

BASE AGENT (claudeclockwork/agents/base_agent.py) - SAMPLE:
{chr(10).join(base_agent.split(chr(10))[:40])}

TASK:
Identify and list:
1. Core patterns for autonomous agents (classes, methods, error handling)
2. Task execution patterns (section(), log(), read_file(), write_file(), run_ollama(), git operations)
3. Hybrid Python + Ollama patterns (when to use Python vs Ollama)
4. Iterative generation patterns (1 item per call, not bulk)
5. Validation and testing patterns
6. Commit and version control patterns
7. Configuration patterns (models, timeouts, resource limits)

Output as structured list of RULES and PATTERNS."""

        analysis = self.run_ollama(prompt)
        self.findings['wos_patterns'] = analysis
        self.log("✓ Analyzed WorldOfShadows patterns")
        return analysis

    def check_claudeclockwork_structure(self):
        """Check ClaudeClockwork directory structure."""
        self.section("Checking ClaudeClockwork Structure")

        if not CW_ROOT.exists():
            self.log("✗ ClaudeClockwork not found at " + str(CW_ROOT))
            self.issues.append("ClaudeClockwork directory not found")
            return False

        self.log("✓ ClaudeClockwork found at " + str(CW_ROOT))

        # Check key directories
        dirs_to_check = [
            "claudeclockwork/agents",
            "claudeclockwork/agents/implementations",
            "claudeclockwork/config",
            "claudeclockwork/utils",
        ]

        for dir_path in dirs_to_check:
            full_path = CW_ROOT / dir_path
            if full_path.exists():
                self.log(f"✓ {dir_path}")
            else:
                self.log(f"✗ {dir_path}")
                self.issues.append(f"Missing directory: {dir_path}")

        return True

    def validate_against_patterns(self, patterns: str):
        """Use Ollama to validate ClaudeClockwork against identified patterns."""
        self.section("Validating ClaudeClockwork Against Patterns")

        # Read ClaudeClockwork key files
        base_agent = self.read_file(CW_ROOT / "claudeclockwork/agents/base_agent.py")
        orchestrator = self.read_file(CW_ROOT / "claudeclockwork/agents/orchestrator.py")
        example = self.read_file(CW_ROOT / "claudeclockwork/agents/implementations/example.py")

        prompt = f"""Validate ClaudeClockwork implementation against WorldOfShadows patterns.

IDENTIFIED PATTERNS (from WorldOfShadows):
{patterns[:2000]}

CLAUDECLOCKWORK CURRENT IMPLEMENTATION:

base_agent.py (sample):
{chr(10).join(base_agent.split(chr(10))[:35])}

orchestrator.py (sample):
{chr(10).join(orchestrator.split(chr(10))[:30])}

example.py (sample):
{chr(10).join(example.split(chr(10))[:30])}

VALIDATION CHECKLIST:
1. Does BaseAgent have: log(), section(), read_file(), write_file(), run_ollama(), git_add(), git_commit()?
2. Does BaseAgent handle errors gracefully with try/except?
3. Does it support iterative generation (1 task per Ollama call)?
4. Does orchestrator track completed and failed tasks?
5. Is there task decomposition support?
6. Are there rate limiting / timeout controls?
7. Is there cost tracking capability?
8. Is there proper logging and reporting?

Output:
- MATCHES: List what correctly matches patterns
- MISSING: List what should be added to match patterns
- RECOMMENDATIONS: What needs to be updated/enhanced"""

        validation = self.run_ollama(prompt)
        self.findings['validation'] = validation
        self.log("✓ Validation completed")
        return validation

    def identify_required_updates(self):
        """Identify what needs to be updated in ClaudeClockwork."""
        self.section("Identifying Required Updates")

        validation = self.findings.get('validation', '')

        prompt = f"""Based on the validation results, identify specific updates needed for ClaudeClockwork.

VALIDATION RESULTS:
{validation[:1500]}

TASK:
Generate a structured list of required updates:

FORMAT:
## File: [path]
- [specific change needed]
- [another change]

Cover:
1. BaseAgent class enhancements
2. Orchestrator improvements
3. New utility functions needed
4. Configuration updates
5. Error handling patterns
6. Documentation/comments needed
7. Test patterns to add
8. Helper functions to add

Be specific with code locations and what to change."""

        updates = self.run_ollama(prompt)
        self.findings['required_updates'] = updates
        self.log("✓ Identified required updates")
        return updates

    def generate_update_plan(self):
        """Generate a prioritized update plan."""
        self.section("Generating Update Plan")

        updates = self.findings.get('required_updates', '')

        prompt = f"""Create a prioritized action plan to update ClaudeClockwork.

REQUIRED UPDATES:
{updates[:1500]}

TASK:
Generate a prioritized action plan with:
1. PRIORITY LEVEL (Critical/High/Medium/Low)
2. DESCRIPTION
3. AFFECTED FILES
4. ESTIMATED COMPLEXITY (1-5)

Start with:
1. Critical fixes (blocking other work)
2. Core pattern implementations
3. Enhancements
4. Documentation

Format as numbered list with clear descriptions."""

        plan = self.run_ollama(prompt)
        self.findings['update_plan'] = plan
        return plan

    def run(self):
        """Execute full validation workflow."""
        print("\n" + "="*70)
        print("  CLAUDECLOCKWORK PATTERN VALIDATION AGENT")
        print("="*70)

        # Phase 1: Analyze WorldOfShadows patterns
        patterns = self.analyze_wos_patterns()

        # Phase 2: Check ClaudeClockwork structure
        if not self.check_claudeclockwork_structure():
            self.log("\n✗ ClaudeClockwork structure incomplete")
            return False

        # Phase 3: Validate against patterns
        validation = self.validate_against_patterns(patterns)

        # Phase 4: Identify updates
        updates = self.identify_required_updates()

        # Phase 5: Generate plan
        plan = self.generate_update_plan()

        # Phase 6: Report
        self.section("VALIDATION REPORT")

        print("\n📋 PATTERNS IDENTIFIED:")
        print(patterns[:800])
        print("\n" + "-"*70)

        print("\n✓ VALIDATION RESULTS:")
        print(validation[:800])
        print("\n" + "-"*70)

        print("\n📝 REQUIRED UPDATES:")
        print(updates[:1000])
        print("\n" + "-"*70)

        print("\n🎯 UPDATE PLAN:")
        print(plan[:1200])

        print("\n" + "="*70)
        if self.issues:
            print(f"  ⚠ ISSUES FOUND: {len(self.issues)}")
            for issue in self.issues:
                print(f"    - {issue}")
        else:
            print("  ✓ Structure validated")
        print("="*70 + "\n")

        # Return full findings for potential implementation
        return {
            'patterns': patterns,
            'validation': validation,
            'updates': updates,
            'plan': plan,
            'issues': self.issues,
        }


if __name__ == "__main__":
    import sys
    agent = PatternValidationAgent()
    results = agent.run()

    # Save results for reference
    if results and isinstance(results, dict):
        print("\n✓ Validation complete - results available for agent implementation")

    sys.exit(0)
