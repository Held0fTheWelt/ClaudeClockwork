#!/usr/bin/env python3
"""
Simple BaseAgent structure fix - move section() inside class.
"""

from pathlib import Path

base_file = Path("/mnt/d/ClaudeClockwork/claudeclockwork/agents/base_agent.py")

if base_file.exists():
    content = base_file.read_text()
    lines = content.split('\n')
    
    # Find section() def outside class
    section_line = -1
    class_line = -1
    
    for i, line in enumerate(lines):
        if "def section(self" in line and "class" not in line:
            section_line = i
        if "class BaseAgent:" in line:
            class_line = i
    
    if section_line >= 0 and section_line < class_line:
        # section() is before class - need to move it inside
        print("  Fixing BaseAgent structure...")
        
        # Extract section() method (3 lines)
        section_lines = []
        for i in range(section_line, min(section_line + 5, len(lines))):
            if lines[i].strip() and not lines[i].startswith("def") and i > section_line:
                continue
            section_lines.append(lines[i])
            if i > section_line and lines[i].startswith("def "):
                break
        
        # Remove section() from before class
        new_lines = []
        skip = False
        for i, line in enumerate(lines):
            if i == section_line:
                skip = True
                continue
            if skip and "class BaseAgent:" in line:
                skip = False
            if not skip:
                new_lines.append(line)
        
        # Find log() method and insert section() before it
        final_lines = []
        for i, line in enumerate(new_lines):
            if "def log(self" in line and i > 0:
                # Insert section() with proper indentation
                final_lines.append("    def section(self, title: str):")
                final_lines.append("        '''Format section headers with separators.'''")
                final_lines.append('        print(f"\\n{\'-\'*70}")')
                final_lines.append('        print(f"  {title}")')
                final_lines.append('        print(f"{\'-\'*70}")')
                final_lines.append("")
            final_lines.append(line)
        
        base_file.write_text('\n'.join(final_lines))
        print("  ✓ Fixed BaseAgent structure")
    else:
        print("  ✓ BaseAgent structure is correct")
else:
    print("  ✗ BaseAgent file not found")
