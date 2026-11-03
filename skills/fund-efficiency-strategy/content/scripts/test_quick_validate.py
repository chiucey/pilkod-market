#!/usr/bin/env python3
"""Regression tests for quick_validate.py."""

import shutil
import tempfile
from pathlib import Path
from unittest import TestCase, main

import quick_validate


class TestQuickValidate(TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="skill_validate_test_"))

    def tearDown(self) -> None:
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def _create_valid_skill(self, name: str = "demo-skill") -> Path:
        skill_dir = self.temp_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: test description\n---\n# Demo\n",
            encoding="utf-8",
        )
        (skill_dir / "_meta.json").write_text(
            '{"id":"skill_123","version":"1.0.0"}\n',
            encoding="utf-8",
        )
        return skill_dir

    def test_valid_skill(self) -> None:
        skill_dir = self._create_valid_skill()
        valid, message = quick_validate.validate_skill(skill_dir)
        self.assertTrue(valid, message)

    def test_missing_meta_file(self) -> None:
        skill_dir = self._create_valid_skill("missing-meta")
        (skill_dir / "_meta.json").unlink()
        valid, message = quick_validate.validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertEqual(message, "_meta.json not found")

    def test_invalid_semver(self) -> None:
        skill_dir = self._create_valid_skill("bad-version")
        (skill_dir / "_meta.json").write_text(
            '{"id":"skill_123","version":"v1"}\n',
            encoding="utf-8",
        )
        valid, message = quick_validate.validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertIn("not valid semver", message)

    def test_directory_name_must_match_frontmatter(self) -> None:
        skill_dir = self._create_valid_skill("folder-name")
        (skill_dir / "SKILL.md").write_text(
            "---\nname: different-name\ndescription: x\n---\n# Demo\n",
            encoding="utf-8",
        )
        valid, message = quick_validate.validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertIn("must match frontmatter name", message)


if __name__ == "__main__":
    main()
