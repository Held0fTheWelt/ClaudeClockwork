#!/usr/bin/env python3
"""
Generate comprehensive skill navigation index.

Usage:
    python3 .claude/tools/skills/generate_skills_index.py

Outputs:
    .claude/skills/_index.json (machine-readable)
    .claude/skills/INDEX.md (human-readable)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Setup import path
# .claude/tools/skills/generate_skills_index.py -> go up 4 levels to repo root
repo_root = Path(__file__).resolve().parent.parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

try:
    from claudeclockwork.runtime import build_registry
except ModuleNotFoundError:
    # Fallback: manually scan skills directory
    build_registry = None


def extract_skill_metadata_from_manifest(manifest_path: Path, skill_id: str, category: str):
    """Extract metadata from a manifest.json file."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    except Exception:
        manifest_data = {}

    return {
        "id": skill_id,
        "category": category,
        "description": manifest_data.get("description", ""),
        "entrypoint": manifest_data.get("entrypoint", ""),
        "frequency": manifest_data.get("frequency", "extended"),
        "path": str(manifest_path.parent),
    }


def scan_skills_directory(skills_root: Path) -> list:
    """Scan skills directory and find all manifest.json files."""
    skills = []

    for manifest_file in sorted(skills_root.rglob("manifest.json")):
        # Skip internal directories (like __pycache__, _event_logger, but NOT .claude or .project)
        has_internal = any(
            (part.startswith("_") and not part.startswith("__"))
            for part in manifest_file.parent.parts
        )
        if has_internal:
            continue

        # Extract category and skill_id from path
        # Path structure: .claude/skills/<category>/<skill_id>/manifest.json
        relative_path = manifest_file.relative_to(skills_root)
        parts = relative_path.parts[:-1]  # Remove manifest.json

        if len(parts) == 2:
            category, skill_id = parts
            skill_meta = extract_skill_metadata_from_manifest(manifest_file, skill_id, category)
            skills.append(skill_meta)

    return sorted(skills, key=lambda s: (s["category"], s["id"]))


def generate_json_index(repo_root: Path) -> dict:
    """Generate machine-readable JSON index."""
    version_file = repo_root / ".claude" / "VERSION"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"

    skills_root = repo_root / ".claude" / "skills"

    # Scan skills directory
    skills = scan_skills_directory(skills_root)

    # Count by category
    categories = defaultdict(int)
    for skill in skills:
        categories[skill["category"]] += 1

    index = {
        "metadata": {
            "version": version,
            "generated": datetime.utcnow().isoformat() + "Z",
            "total_skills": len(skills),
            "categories_count": len(categories),
        },
        "skills": skills,
        "categories": dict(sorted(categories.items())),
    }

    return index


def generate_markdown_index(index: dict) -> str:
    """Generate human-readable markdown index."""
    md = """# Skills Navigation Index

**Generated:** """ + index["metadata"]["generated"] + """
**Version:** """ + index["metadata"]["version"] + """
**Total Skills:** """ + str(index["metadata"]["total_skills"]) + """

---

## Quick Navigation

### By Category

"""

    # Group skills by category
    categories_map = defaultdict(list)
    for skill in index["skills"]:
        categories_map[skill["category"]].append(skill)

    for category in sorted(categories_map.keys()):
        skills = categories_map[category]
        md += f"\n### 📁 {category.title()} ({len(skills)} skills)\n\n"
        for skill in skills:
            freq = skill.get("frequency", "extended")
            freq_icon = "⭐" if freq == "core" else "·"
            md += f"- {freq_icon} **{skill['id']}** — {skill['description'][:60]}\n"

    md += """

---

## By Frequency

### ⭐ Core Skills (High-Frequency)

Frequently used in daily workflows:

"""

    core_skills = [s for s in index["skills"] if s.get("frequency") == "core"]
    for skill in core_skills:
        md += f"- **{skill['id']}** (`{skill['category']}`)\n"

    md += """

### · Extended Skills (Specialized)

Domain-specific or less frequent use:

"""

    extended_skills = [s for s in index["skills"] if s.get("frequency") != "core"]
    for skill in extended_skills[:20]:  # Show first 20
        md += f"- **{skill['id']}** (`{skill['category']}`)\n"
    md += f"\n... and {len(extended_skills) - 20} more extended skills.\n"

    md += """

---

## All Skills (Alphabetical)

"""

    for skill in sorted(index["skills"], key=lambda s: s["id"]):
        md += f"- `{skill['id']}` — {skill['description'][:70]}\n"

    md += """

---

## Usage

### Find a Skill by Name

Use Ctrl+F to search this page for a skill name.

### Find Skills by Category

See "By Category" section above.

### Find Core Skills

See "By Frequency" section for frequently-used skills.

### Full Metadata (JSON)

For programmatic access, use `_index.json`:

```bash
python3 -m json.tool .claude/skills/_index.json
```

---

## Adding a New Skill

1. Create skill implementation: `.claude/tools/skills/<skill>.py`
2. Create manifest: `.claude/skills/<category>/<skill>/manifest.json`
3. Create skill.py wrapper: `.claude/skills/<category>/<skill>/skill.py`
4. Run: `python3 .claude/tools/skills/generate_skills_index.py`
5. Commit changes

---

**Last Updated:** """ + index["metadata"]["generated"] + """
"""

    return md


def main() -> int:
    """Generate skill index files."""
    # Get repo root using CWD if available
    repo_root = Path.cwd()
    if not (repo_root / ".claude" / "skills").exists():
        # Fallback: use script location
        repo_root = Path(__file__).resolve().parent.parent.parent.parent

    try:
        # Generate index
        index = generate_json_index(repo_root)

        # Write JSON index
        json_path = repo_root / ".claude" / "skills" / "_index.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✅ JSON index written to {json_path}")

        # Write markdown index
        md_content = generate_markdown_index(index)
        md_path = repo_root / ".claude" / "skills" / "INDEX.md"
        md_path.write_text(md_content, encoding="utf-8")
        print(f"✅ Markdown index written to {md_path}")

        print(f"\n📊 Summary:")
        print(f"   Total Skills: {index['metadata']['total_skills']}")
        print(f"   Categories: {index['metadata']['categories_count']}")
        print(f"   Version: {index['metadata']['version']}")

        return 0
    except Exception as exc:
        print(f"❌ Error: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
