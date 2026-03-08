"""
Tests for skills navigation index (MVP 19).
"""

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
INDEX_JSON = ROOT / ".claude" / "skills" / "_index.json"
INDEX_MD = ROOT / ".claude" / "skills" / "INDEX.md"


class TestSkillsIndex:
    """Verify skills index is complete and deterministic."""

    def test_index_json_exists(self) -> None:
        """Index JSON file must exist."""
        assert INDEX_JSON.exists(), f"Index JSON not found at {INDEX_JSON}"

    def test_index_json_valid(self) -> None:
        """Index JSON must parse as valid JSON."""
        try:
            with open(INDEX_JSON, "r", encoding="utf-8") as f:
                index = json.load(f)
        except json.JSONDecodeError as exc:
            pytest.fail(f"Index JSON is invalid: {exc}")
        assert index is not None

    def test_index_json_completeness(self) -> None:
        """Index JSON must include required fields."""
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            index = json.load(f)

        required_keys = {"metadata", "skills", "categories"}
        assert required_keys.issubset(set(index.keys())), (
            f"Index missing keys: {required_keys - set(index.keys())}"
        )

        # Check metadata
        assert "total_skills" in index["metadata"]
        assert "version" in index["metadata"]
        assert "categories_count" in index["metadata"]

        # Check skills
        assert isinstance(index["skills"], list)
        assert len(index["skills"]) > 0

    def test_index_skill_count(self) -> None:
        """Index must contain 109 skills."""
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            index = json.load(f)

        assert index["metadata"]["total_skills"] == 109, (
            f"Expected 109 skills, found {index['metadata']['total_skills']}"
        )

    def test_index_skill_format(self) -> None:
        """Each skill must have required fields."""
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            index = json.load(f)

        required_skill_keys = {"id", "category", "entrypoint", "frequency"}
        for skill in index["skills"]:
            assert required_skill_keys.issubset(set(skill.keys())), (
                f"Skill {skill.get('id')} missing keys: "
                f"{required_skill_keys - set(skill.keys())}"
            )

    def test_index_stable_ordering(self) -> None:
        """Index skills must be stably ordered by category then id."""
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            index = json.load(f)

        skills = index["skills"]
        ordered_skills = sorted(skills, key=lambda s: (s["category"], s["id"]))

        # Compare IDs in order
        actual_ids = [s["id"] for s in skills]
        expected_ids = [s["id"] for s in ordered_skills]

        assert actual_ids == expected_ids, (
            "Skills are not in stable order (category, then id)"
        )

    def test_index_md_exists(self) -> None:
        """Index markdown file must exist."""
        assert INDEX_MD.exists(), f"Index markdown not found at {INDEX_MD}"

    def test_index_md_readable(self) -> None:
        """Index markdown must be readable and non-empty."""
        content = INDEX_MD.read_text(encoding="utf-8")
        assert len(content) > 0, "Index markdown is empty"
        assert "# Skills Navigation Index" in content, (
            "Index markdown missing title"
        )

    def test_index_md_mentions_all_skills(self) -> None:
        """Index markdown should reference all skills."""
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            index = json.load(f)

        md_content = INDEX_MD.read_text(encoding="utf-8")
        skill_count = 0

        for skill in index["skills"]:
            if f"`{skill['id']}`" in md_content or f"**{skill['id']}**" in md_content:
                skill_count += 1

        assert skill_count >= 100, (
            f"Markdown only references {skill_count}/109 skills"
        )

    def test_index_deterministic_regeneration(self) -> None:
        """Regenerating the index must produce identical content (excluding timestamp)."""
        import subprocess

        # Get current index
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            original = json.load(f)

        # Regenerate
        script = ROOT / ".claude" / "tools" / "skills" / "generate_skills_index.py"
        result = subprocess.run(
            [
                "python3",
                str(script),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Index regeneration failed: {result.stderr}"

        # Compare (excluding timestamp which is expected to change)
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            regenerated = json.load(f)

        # Compare metadata except generated timestamp
        assert (
            original["metadata"]["total_skills"]
            == regenerated["metadata"]["total_skills"]
        )
        assert (
            original["metadata"]["categories_count"]
            == regenerated["metadata"]["categories_count"]
        )

        # Compare skills list
        assert original["skills"] == regenerated["skills"], (
            "Regenerated skills list differs from original"
        )

        # Compare categories
        assert original["categories"] == regenerated["categories"], (
            "Regenerated categories differ from original"
        )
