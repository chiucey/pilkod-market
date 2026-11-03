#!/usr/bin/env python3
"""
Test script for K-Dense BYOK Skill validation and packaging
"""

import unittest
import json
import os
import tempfile
import shutil
from pathlib import Path


class TestSkillStructure(unittest.TestCase):
    """Test skill directory structure"""

    @classmethod
    def setUpClass(cls):
        cls.skill_path = Path(__file__).parent.parent

    def test_skill_md_exists(self):
        """SKILL.md should exist"""
        self.assertTrue((self.skill_path / 'SKILL.md').exists())

    def test_meta_json_exists(self):
        """_meta.json should exist"""
        self.assertTrue((self.skill_path / '_meta.json').exists())

    def test_scripts_directory_exists(self):
        """scripts/ directory should exist"""
        self.assertTrue((self.skill_path / 'scripts').is_dir())

    def test_references_directory_exists(self):
        """references/ directory should exist"""
        self.assertTrue((self.skill_path / 'references').is_dir())


class TestMetaJson(unittest.TestCase):
    """Test _meta.json format"""

    @classmethod
    def setUpClass(cls):
        cls.skill_path = Path(__file__).parent.parent
        with open(cls.skill_path / '_meta.json', 'r') as f:
            cls.meta = json.load(f)

    def test_meta_has_id(self):
        """_meta.json should have 'id' field"""
        self.assertIn('id', self.meta)

    def test_meta_has_version(self):
        """_meta.json should have 'version' field"""
        self.assertIn('version', self.meta)

    def test_version_format(self):
        """version should follow semver format"""
        import re
        self.assertRegex(self.meta['version'], r'^\d+\.\d+\.\d+$')


class TestFrontmatter(unittest.TestCase):
    """Test SKILL.md frontmatter"""

    @classmethod
    def setUpClass(cls):
        cls.skill_path = Path(__file__).parent.parent
        with open(cls.skill_path / 'SKILL.md', 'r') as f:
            cls.content = f.read()

    def test_frontmatter_starts_with_yaml(self):
        """SKILL.md should start with ---"""
        self.assertTrue(self.content.startswith('---'))

    def test_frontmatter_has_name(self):
        """Frontmatter should contain name field"""
        self.assertIn('name:', self.content)

    def test_frontmatter_has_description(self):
        """Frontmatter should contain description field"""
        self.assertIn('description:', self.content)


class TestScripts(unittest.TestCase):
    """Test validation and packaging scripts"""

    @classmethod
    def setUpClass(cls):
        cls.skill_path = Path(__file__).parent.parent

    def test_validate_script_exists(self):
        """quick_validate.py should exist"""
        self.assertTrue((self.skill_path / 'scripts' / 'quick_validate.py').exists())

    def test_package_script_exists(self):
        """package_skill.py should exist"""
        self.assertTrue((self.skill_path / 'scripts' / 'package_skill.py').exists())


if __name__ == '__main__':
    unittest.main()
