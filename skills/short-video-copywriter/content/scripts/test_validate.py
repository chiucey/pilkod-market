#!/usr/bin/env python3
"""
Unit tests for viral-copywriter skill validation
"""

import unittest
import os
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from quick_validate import (
    validate_frontmatter,
    validate_meta_json,
    validate_structure
)

SKILL_PATH = str(Path(__file__).parent.parent)


class TestSkillValidation(unittest.TestCase):
    """Test suite for skill validation"""

    def test_frontmatter_exists(self):
        """Frontmatter should exist and be valid"""
        passed, errors = validate_frontmatter(SKILL_PATH)
        self.assertTrue(passed, f"Frontmatter validation failed: {errors}")

    def test_meta_json_exists(self):
        """_meta.json should exist and be valid"""
        passed, errors = validate_meta_json(SKILL_PATH)
        self.assertTrue(passed, f"Meta JSON validation failed: {errors}")

    def test_structure_valid(self):
        """Directory structure should be valid"""
        passed, errors = validate_structure(SKILL_PATH)
        self.assertTrue(passed, f"Structure validation failed: {errors}")

    def test_skill_name_matches(self):
        """Skill name in frontmatter should match folder"""
        skill_md = Path(SKILL_PATH) / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        import re
        name_match = re.search(r"name:\s*(.+)", content)
        if name_match:
            name = name_match.group(1).strip()
            folder_name = Path(SKILL_PATH).name
            self.assertEqual(name, folder_name,
                           f"Name mismatch: {name} vs {folder_name}")


class TestSkillReferences(unittest.TestCase):
    """Test suite for skill references"""

    def test_references_exist(self):
        """Reference files should exist"""
        references = Path(SKILL_PATH) / "references"
        self.assertTrue(references.exists(), "references/ not found")

        templates = references / "copywriting-templates.md"
        guides = references / "platform-guides.md"
        rubrics = references / "score-rubrics.md"

        self.assertTrue(templates.exists(), "copywriting-templates.md missing")
        self.assertTrue(guides.exists(), "platform-guides.md missing")
        self.assertTrue(rubrics.exists(), "score-rubrics.md missing")

    def test_assets_exist(self):
        """Asset files should exist"""
        assets = Path(SKILL_PATH) / "assets"
        self.assertTrue(assets.exists(), "assets/ not found")

        examples = assets / "style-examples.md"
        self.assertTrue(examples.exists(), "style-examples.md missing")


class TestSkillScripts(unittest.TestCase):
    """Test suite for skill scripts"""

    def test_scripts_exist(self):
        """Script files should exist"""
        scripts = Path(SKILL_PATH) / "scripts"
        self.assertTrue(scripts.exists(), "scripts/ not found")

        validate_script = scripts / "quick_validate.py"
        package_script = scripts / "package_skill.py"

        self.assertTrue(validate_script.exists(), "quick_validate.py missing")
        self.assertTrue(package_script.exists(), "package_skill.py missing")


if __name__ == "__main__":
    unittest.main(verbosity=2)
