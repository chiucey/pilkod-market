#!/usr/bin/env python3
"""
Viral Script Creator - Skill Tests
"""

import unittest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class TestValidator(unittest.TestCase):
    """测试验证器功能"""

    def setUp(self):
        self.skill_path = Path(__file__).parent.parent.resolve()

    def test_skill_md_exists(self):
        sk_path = self.skill_path / "SKILL.md"
        self.assertTrue(sk_path.exists())

    def test_meta_exists(self):
        meta_path = self.skill_path / "_meta.json"
        self.assertTrue(meta_path.exists())

    def test_meta_valid_json(self):
        meta_path = self.skill_path / "_meta.json"
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        self.assertIn('id', meta)
        self.assertIn('version', meta)

    def test_frontmatter_format(self):
        from quick_validate import validate_frontmatter
        passed, msg = validate_frontmatter(self.skill_path)
        self.assertTrue(passed, f"Frontmatter validation failed: {msg}")


class TestPackager(unittest.TestCase):
    """测试打包器功能"""

    def setUp(self):
        self.skill_path = Path(__file__).parent.parent.resolve()
        self.output_path = self.skill_path.parent / "test_viral_output.skill"

    def tearDown(self):
        if self.output_path.exists():
            self.output_path.unlink()

    def test_package_creates_file(self):
        from package_skill import package_skill
        passed, result = package_skill(self.skill_path, self.output_path)
        self.assertTrue(passed)
        self.assertTrue(self.output_path.exists())

    def test_package_contains_required_files(self):
        from package_skill import package_skill
        import zipfile
        passed, result = package_skill(self.skill_path, self.output_path)
        self.assertTrue(passed)
        with zipfile.ZipFile(self.output_path, 'r') as zf:
            file_list = zf.namelist()
            self.assertTrue(any('SKILL.md' in f for f in file_list))
            self.assertTrue(any('_meta.json' in f for f in file_list))


if __name__ == "__main__":
    unittest.main(verbosity=2)
