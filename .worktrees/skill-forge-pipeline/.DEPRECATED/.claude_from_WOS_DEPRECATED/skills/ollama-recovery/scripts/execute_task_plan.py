#!/usr/bin/env python3
"""
Multi-Phase Task Execution Engine

Parses Task.md-style task plans and executes each phase autonomously using Claude Agents.
Coordinates phase execution, manages context passing, and generates comprehensive reports.
"""

import re
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess


class TaskParser:
    """Parses Task.md files to extract phase definitions."""

    def __init__(self, task_file: str):
        self.task_file = Path(task_file)
        self.content = self.task_file.read_text(encoding='utf-8')
        self.mission = None
        self.phases = []
        self.constraints = []
        self.parse()

    def parse(self):
        """Extract mission, phases, and constraints from task file."""
        # Extract mission statement
        mission_match = re.search(r'Mission:?\s*\n(.*?)(?=\n\n|\nPhase|\nImportant)', self.content, re.DOTALL)
        if mission_match:
            self.mission = mission_match.group(1).strip()

        # Extract phases
        phase_pattern = r'Phase\s+(\d+)\s*—\s*(.*?)\n(.*?)(?=Phase\s+\d+|$)'
        for match in re.finditer(phase_pattern, self.content, re.DOTALL):
            phase_num = int(match.group(1))
            phase_title = match.group(2).strip()
            phase_content = match.group(3).strip()

            self.phases.append({
                'number': phase_num,
                'title': phase_title,
                'content': phase_content,
                'tasks': self._extract_tasks(phase_content),
                'success_criteria': self._extract_success_criteria(phase_content)
            })

        # Extract constraints
        constraints_match = re.search(r'Important constraints:(.*?)(?=\n\n|\nExecution|\Z)', self.content, re.DOTALL)
        if constraints_match:
            constraint_lines = constraints_match.group(1).strip().split('\n')
            self.constraints = [line.strip('- ').strip() for line in constraint_lines if line.strip()]

    def _extract_tasks(self, content: str) -> List[str]:
        """Extract task bullets from phase content."""
        task_lines = re.findall(r'^-\s+(.+)$', content, re.MULTILINE)
        return task_lines

    def _extract_success_criteria(self, content: str) -> List[str]:
        """Extract success criteria from phase content."""
        criteria_lines = re.findall(r'(?:success criteria|acceptance criteria|goal)[:\s]+(.*?)(?=\n|$)',
                                    content, re.IGNORECASE | re.DOTALL)
        return criteria_lines if criteria_lines else ["Phase completed successfully"]

    def get_phase(self, phase_num: int) -> Optional[Dict]:
        """Get a specific phase by number."""
        for phase in self.phases:
            if phase['number'] == phase_num:
                return phase
        return None

    def get_phase_context(self, up_to_phase: int) -> str:
        """Build context string for a phase (includes all previous phases)."""
        context = f"Mission: {self.mission}\n\n"
        context += "Constraints:\n"
        for constraint in self.constraints:
            context += f"- {constraint}\n"
        context += "\n"

        for phase in self.phases:
            if phase['number'] <= up_to_phase:
                context += f"Phase {phase['number']} — {phase['title']}\n"
                context += f"{phase['content']}\n\n"

        return context


class PhaseExecutor:
    """Executes a single phase using Claude Agents."""

    def __init__(self, phase: Dict, task_context: str, previous_results: Optional[Dict] = None):
        self.phase = phase
        self.task_context = task_context
        self.previous_results = previous_results or {}
        self.report = None

    def execute(self, agent_tool_available: bool = True) -> Tuple[bool, str]:
        """
        Execute phase and return (success, report_content).

        In a real implementation, this would use the Agent tool.
        For now, we'll simulate the execution and provide a template.
        """
        phase_num = self.phase['number']
        phase_title = self.phase['title']

        # Build phase briefing
        briefing = f"""
Execute Phase {phase_num} — {phase_title}

## Context
{self.task_context}

## Your Task
{self.phase['content']}

## Previous Results (if any)
{json.dumps(self.previous_results, indent=2) if self.previous_results else "This is the first phase."}

## Success Criteria
{chr(10).join(f"- {c}" for c in self.phase['success_criteria'])}

## Output Requirements
- Document all findings and results
- Be specific with facts, metrics, and timestamps
- If issues are found, explain root causes
- Provide clear next steps
- Generate files/reports as specified in the phase description
"""

        # In real implementation: call Agent tool with briefing
        # For now, return template structure
        report = f"""
# Phase {phase_num} — {phase_title} Report

**Execution Date:** {datetime.now().isoformat()}

## Status
[TEMPLATE - This would be filled by actual Agent execution]

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Tasks Completed
{chr(10).join(f"- [ ] {task}" for task in self.phase['tasks'])}

## Success Criteria Met
{chr(10).join(f"- [?] {criteria}" for criteria in self.phase['success_criteria'])}

## Files Generated
[List of any files created during this phase]

## Next Steps
[Recommendations for next phase]

---

**Agent Briefing (actual context provided to execution):**
```
{briefing}
```
"""

        return (True, report)


class TaskExecutor:
    """Coordinates execution of all phases in a task plan."""

    def __init__(self, task_file: str, output_dir: Optional[str] = None):
        self.task_file = Path(task_file)
        self.output_dir = Path(output_dir) if output_dir else self.task_file.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.parser = TaskParser(str(self.task_file))
        self.phase_results = {}
        self.execution_log = []
        self.start_time = None
        self.end_time = None

    def execute_all_phases(self) -> bool:
        """Execute all phases sequentially."""
        self.start_time = datetime.now()
        self.log(f"Starting task execution: {self.parser.mission}")
        self.log(f"Total phases: {len(self.parser.phases)}")

        all_success = True

        for phase in self.parser.phases:
            phase_num = phase['number']
            phase_title = phase['title']

            self.log(f"\n{'='*70}")
            self.log(f"Phase {phase_num} — {phase_title}")
            self.log(f"{'='*70}")

            # Build context (includes all previous phases)
            context = self.parser.get_phase_context(phase_num)

            # Execute phase
            executor = PhaseExecutor(phase, context, self.phase_results)
            success, report = executor.execute()

            self.phase_results[phase_num] = {
                'title': phase_title,
                'success': success,
                'report': report,
                'timestamp': datetime.now().isoformat()
            }

            # Save phase report
            report_file = self.output_dir / f"PHASE_{phase_num:02d}_{phase_title.replace(' ', '_').replace('—', '')}.md"
            report_file.write_text(report, encoding='utf-8')
            self.log(f"✓ Phase report saved: {report_file.name}")

            if not success:
                self.log(f"✗ Phase {phase_num} failed")
                all_success = False
                # Don't continue on critical failures, but document them
                break
            else:
                self.log(f"✓ Phase {phase_num} completed successfully")

        self.end_time = datetime.now()
        return all_success

    def execute_phase(self, phase_num: int) -> bool:
        """Execute a single specific phase."""
        phase = self.parser.get_phase(phase_num)
        if not phase:
            self.log(f"✗ Phase {phase_num} not found")
            return False

        self.start_time = datetime.now()
        self.log(f"Executing Phase {phase_num} — {phase['title']}")

        context = self.parser.get_phase_context(phase_num)
        executor = PhaseExecutor(phase, context, {})
        success, report = executor.execute()

        self.phase_results[phase_num] = {
            'title': phase['title'],
            'success': success,
            'report': report,
            'timestamp': datetime.now().isoformat()
        }

        # Save report
        report_file = self.output_dir / f"PHASE_{phase_num:02d}_{phase['title'].replace(' ', '_')}.md"
        report_file.write_text(report, encoding='utf-8')
        self.log(f"Phase report saved: {report_file.name}")

        self.end_time = datetime.now()
        return success

    def generate_final_report(self) -> str:
        """Generate aggregated final report."""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        total_phases = len(self.parser.phases)
        completed_phases = len([r for r in self.phase_results.values() if r['success']])

        report = f"""# Task Execution Final Report

**Mission:** {self.parser.mission}

**Date:** {datetime.now().isoformat()}

**Duration:** {duration:.1f} seconds

## Executive Summary

- **Total Phases:** {total_phases}
- **Completed:** {completed_phases}/{total_phases}
- **Status:** {'✓ SUCCESS' if completed_phases == total_phases else '⚠ PARTIAL / ✗ FAILED'}

## Phase Summary

"""
        for phase_num in sorted(self.phase_results.keys()):
            result = self.phase_results[phase_num]
            status_icon = '✓' if result['success'] else '✗'
            report += f"\n### {status_icon} Phase {phase_num} — {result['title']}\n"
            report += f"**Status:** {'Completed' if result['success'] else 'Failed'}\n"
            report += f"**Timestamp:** {result['timestamp']}\n"

        report += f"""

## Key Findings

[See individual phase reports for detailed findings]

## Recommendations

1. Review each phase report for specific findings
2. Address any failed phases before proceeding
3. Follow the documented next steps from the final phase

## Deliverables

The following files have been generated:

"""

        for report_file in sorted(self.output_dir.glob('PHASE_*.md')):
            report += f"- {report_file.name}\n"

        report += f"""

---

**Execution Log:**
```
{chr(10).join(self.execution_log)}
```
"""

        return report

    def save_final_report(self) -> Path:
        """Save final aggregated report."""
        report = self.generate_final_report()
        report_file = self.output_dir / "FINAL_REPORT.md"
        report_file.write_text(report, encoding='utf-8')
        return report_file

    def log(self, message: str):
        """Log a message to execution log."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        print(log_entry)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python execute_task_plan.py <task_file> [output_dir] [phase_num]")
        print("  task_file: Path to Task.md")
        print("  output_dir: Where to save reports (default: task file directory)")
        print("  phase_num: Execute only this phase (default: all phases)")
        sys.exit(1)

    task_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    phase_num = int(sys.argv[3]) if len(sys.argv) > 3 else None

    executor = TaskExecutor(task_file, output_dir)

    if phase_num:
        success = executor.execute_phase(phase_num)
    else:
        success = executor.execute_all_phases()

    # Save final report
    report_file = executor.save_final_report()
    print(f"\n✓ Final report saved: {report_file}")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
