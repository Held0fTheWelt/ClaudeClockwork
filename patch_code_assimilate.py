#!/usr/bin/env python3
"""Patch script to add agent_type field to code_assimilate manifest."""

with open('.claude/skills/analysis/code_assimilate/manifest.json', 'r') as f:
    content = f.read()

old = '  "trust_level": "local",\n  "inputs": {},'
new = '  "trust_level": "local",\n  "agent_type": "ollama",\n  "inputs": {},'

if old in content:
    content = content.replace(old, new)
    with open('.claude/skills/analysis/code_assimilate/manifest.json', 'w') as f:
        f.write(content)
    print("✓ Patched code_assimilate manifest")
else:
    print("✗ Could not find replacement point")
