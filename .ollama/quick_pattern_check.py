#!/usr/bin/env python3
"""
Quick pattern validation - small, focused, efficient.
"""

import subprocess
from pathlib import Path

WOS_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
CW_ROOT = Path("/mnt/d/ClaudeClockwork")

print("\n" + "="*70)
print("  QUICK PATTERN VALIDATION")
print("="*70 + "\n")

# Check BaseAgent in both places
print("Checking BaseAgent patterns:\n")

wos_base = (WOS_ROOT / "claudeclockwork/agents/base_agent.py").read_text()
cw_base = (CW_ROOT / "claudeclockwork/agents/base_agent.py").read_text()

patterns = ["def log(", "def section(", "def read_file(", "def write_file(", "def run_ollama(", "def git_add(", "def git_commit("]

print("WorldOfShadows BaseAgent:")
for p in patterns:
    has = "✓" if p in wos_base else "✗"
    print(f"  {has} {p}")

print("\nClaudeClockwork BaseAgent:")
for p in patterns:
    has = "✓" if p in cw_base else "✗"
    print(f"  {has} {p}")

# Check for Ollama integration patterns
print("\n" + "-"*70)
print("Ollama Integration Patterns:\n")

wos_patterns = [
    ("Error handling with try/except", "except Exception" in wos_base),
    ("Logging with logger", "logger" in wos_base or "print" in wos_base),
    ("JSON parsing support", "json" in wos_base),
    ("Git operations", "subprocess.run" in wos_base),
]

print("WorldOfShadows has:")
for name, present in wos_patterns:
    mark = "✓" if present else "✗"
    print(f"  {mark} {name}")

cw_patterns = [
    ("Error handling with try/except", "except Exception" in cw_base),
    ("Logging with logger", "logger" in cw_base or "print" in cw_base),
    ("JSON parsing support", "json" in cw_base),
    ("Git operations", "subprocess.run" in cw_base),
]

print("\nClaudeClockwork has:")
for name, present in cw_patterns:
    mark = "✓" if present else "✗"
    print(f"  {mark} {name}")

# Check for iterative generation pattern
print("\n" + "-"*70)
print("Iterative Generation Pattern:\n")

wos_agents = list((WOS_ROOT / ".ollama").glob("*.py"))
print(f"WorldOfShadows: {len(wos_agents)} autonomous agents")
print("  - master_corrective_agent_v3.py (Task A, B, C, D)")
print("  - implement_taskexecutor_integration.py")
print("  - master_taskexecutor_validation_agent.py")
print("  - Examples of iterative single-task agents")

cw_examples = list((CW_ROOT / "claudeclockwork/agents/implementations").glob("*.py"))
print(f"\nClaudeClockwork: {len(cw_examples)} example agents")

if len(cw_examples) < 5:
    print("  ⚠ Missing task-specific agent examples")
else:
    print("  ✓ Has multiple agent examples")

# Summary
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)

differences = []

# Check core methods
for p in patterns:
    if p in wos_base and p not in cw_base:
        differences.append(f"Missing in CW: {p}")

# Check patterns
for name, wos_has in wos_patterns:
    cw_has = next((v for n, v in cw_patterns if n == name), False)
    if wos_has and not cw_has:
        differences.append(f"Missing in CW: {name}")

if differences:
    print(f"\n⚠ {len(differences)} DIFFERENCES FOUND:\n")
    for diff in differences:
        print(f"  - {diff}")
else:
    print("\n✓ Patterns match!")

print("\n" + "="*70 + "\n")
