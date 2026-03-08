# Skills Navigation Index

**Generated:** 2026-03-08T00:13:58.382651Z
**Version:** unknown
**Total Skills:** 0

---

## Quick Navigation

### By Category



---

## By Frequency

### ⭐ Core Skills (High-Frequency)

Frequently used in daily workflows:



### · Extended Skills (Specialized)

Domain-specific or less frequent use:


... and -20 more extended skills.


---

## All Skills (Alphabetical)



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

**Last Updated:** 2026-03-08T00:13:58.382651Z
