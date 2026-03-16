#!/usr/bin/env python3
"""
Focused pattern check: Compare agents in .ollama/ with ClaudeClockwork base_agent.
"""

from pathlib import Path

WOS_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
CW_ROOT = Path("/mnt/d/ClaudeClockwork")

print("\n" + "="*70)
print("  PATTERN COMPARISON: .ollama Agents vs ClaudeClockwork BaseAgent")
print("="*70 + "\n")

# Read key files
cw_base = (CW_ROOT / "claudeclockwork/agents/base_agent.py").read_text()

# Sample from actual .ollama agents
corrective = (WOS_ROOT / ".ollama/master_corrective_agent_v3.py").read_text()
taskexec = (WOS_ROOT / ".ollama/implement_taskexecutor_integration.py").read_text()

print("CORE METHOD PATTERNS (present in working .ollama agents):\n")

core_methods = {
    "def log(": "Logging with consistent format",
    "def section(": "Section headers with separator lines",
    "def read_file(": "File reading capability",
    "def write_file(": "File writing capability",
    "def run_ollama(": "Ollama integration",
    "def git_add(": "Git staging",
    "def git_commit(": "Git commits",
}

print("✓ Found in .ollama agents:")
for method, desc in core_methods.items():
    if method in corrective or method in taskexec:
        print(f"  ✓ {method:20} — {desc}")

print("\n ClaudeClockwork BaseAgent currently has:")
for method, desc in core_methods.items():
    if method in cw_base:
        print(f"  ✓ {method:20} — {desc}")
    else:
        print(f"  ✗ {method:20} — {desc}")

print("\n" + "-"*70)
print("INTEGRATION PATTERNS:\n")

patterns = [
    ("try/except error handling", "except Exception", "Robust error handling"),
    ("Ollama model selection", "model=", "Model configuration"),
    ("JSON support", "import json", "JSON parsing"),
    ("Logging", "logger = ", "Logging setup"),
    ("Task decomposition", "def ", "Multiple focused methods"),
    ("Results tracking", "self.results", "Aggregating results"),
    ("File modification tracking", "self.files_modified", "Tracking changes"),
]

print("✓ .ollama agents have:")
for name, keyword, desc in patterns:
    found = keyword in corrective or keyword in taskexec
    mark = "✓" if found else "✗"
    print(f"  {mark} {name:30} — {desc}")

print("\n ClaudeClockwork BaseAgent has:")
for name, keyword, desc in patterns:
    found = keyword in cw_base
    mark = "✓" if found else "✗"
    print(f"  {mark} {name:30} — {desc}")

print("\n" + "-"*70)
print("MISSING FEATURES IN CLAUDECLOCKWORK:\n")

missing = []

# Check for git operations
if "def git_add" not in cw_base:
    missing.append("git_add() method - needed for autonomous commits")
if "def git_commit" not in cw_base:
    missing.append("git_commit() method - needed for autonomous commits")

# Check for proper error handling in run_ollama
if "except" not in cw_base or "Exception" not in cw_base:
    missing.append("Robust exception handling in run_ollama()")

# Check for logging
if "logger" not in cw_base:
    missing.append("Proper logging setup (currently just uses print)")

if missing:
    print("⚠ Missing capabilities:\n")
    for i, item in enumerate(missing, 1):
        print(f"  {i}. {item}")
else:
    print("✓ All core patterns present!")

print("\n" + "="*70)
print("  RECOMMENDATION")
print("="*70 + "\n")

if missing:
    print("ClaudeClockwork BaseAgent needs updates to match production patterns.")
    print("Key additions needed:")
    print("  1. git_add() and git_commit() methods")
    print("  2. Enhanced error handling in run_ollama()")
    print("  3. Proper logging infrastructure")
    print("\nThese are required for autonomous agents to commit their work.")
else:
    print("✓ Patterns match - ClaudeClockwork is ready!")

print("\n" + "="*70 + "\n")
