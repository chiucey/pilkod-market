#!/usr/bin/env python3
"""Regression tests for package_skill.py."""

import shutil
import tempfile
import zipfile
from pathlib import Path
from unittest import TestCase, main

from package_skill import package_skill


class TestPackageSkill(TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="skill_package_test_"))
        self.out_dir = self.temp_dir / "out"
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def _create_valid_skill(self, name: str = "pack-skill") -> Path:
        skill_dir = self.temp_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: package test\n---\n# Demo\n",
            encoding="utf-8",
        )
        (skill_dir / "_meta.json").write_text(
            '{"id":"skill_pkg","version":"1.0.0"}\n',
            encoding="utf-8",
        )
        (skill_dir / "notes.txt").write_text("hello\n", encoding="utf-8")
        return skill_dir

    def test_package_success(self) -> None:
        skill_dir = self._create_valid_skill("package-ok")
        archive = package_skill(skill_dir, self.out_dir)
        self.assertIsNotNone(archive)
        self.assertTrue(archive.exists())
        with zipfile.ZipFile(archive, "r") as zf:
            names = set(zf.namelist())
        self.assertIn("package-ok/SKILL.md", names)
        self.assertIn("package-ok/_meta.json", names)
        self.assertIn("package-ok/notes.txt", names)

    def test_refuse_symlink(self) -> None:
        skill_dir = self._create_valid_skill("package-symlink")
        target = self.temp_dir / "outside.txt"
        target.write_text("secret\n", encoding="utf-8")
        link = skill_dir / "linked.txt"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink is not supported in this environment")

        archive = package_skill(skill_dir, self.out_dir)
        self.assertIsNone(archive)


if __name__ == "__main__":
    main()
