#!/usr/bin/env python3
"""
Skill Validator Script
Validates commercial-project-auto-developer skill structure and content
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class SkillValidator:
    """Validates skill structure and frontmatter compliance"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def validate(self) -> bool:
        """Run all validations"""
        self._check_directory_structure()
        self._check_meta_json()
        self._check_skill_md()
        self._check_naming()
        self._check_assets()

        return len(self.errors) == 0

    def _check_directory_structure(self) -> None:
        """Verify required directories exist"""
        required_dirs = ['scripts', 'references', 'assets']
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists():
                self.warnings.append(f"Missing recommended directory: {dir_name}")
            elif not dir_path.is_dir():
                self.errors.append(f"{dir_name} exists but is not a directory")

    def _check_meta_json(self) -> None:
        """Validate _meta.json structure"""
        meta_path = self.skill_path / '_meta.json'

        if not meta_path.exists():
            self.errors.append("_meta.json not found")
            return

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in _meta.json: {e}")
            return

        required_keys = ['id', 'version']
        for key in required_keys:
            if key not in meta:
                self.errors.append(f"Missing required key in _meta.json: {key}")

        if 'version' in meta:
            if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                self.errors.append("Version must follow semver format (x.y.z)")

        self.passed.append("_meta.json structure valid")

    def _check_skill_md(self) -> None:
        """Validate SKILL.md frontmatter and content"""
        skill_md = self.skill_path / 'SKILL.md'

        if not skill_md.exists():
            self.errors.append("SKILL.md not found")
            return

        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check frontmatter
        if not content.startswith('---'):
            self.errors.append("SKILL.md must start with YAML frontmatter (---)")
            return

        # Extract frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            self.errors.append("Invalid frontmatter format")
            return

        try:
            import yaml
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
        except Exception as e:
            self.errors.append(f"Invalid YAML in frontmatter: {e}")
            return

        # Check required frontmatter keys
        if 'name' not in frontmatter:
            self.errors.append("Frontmatter missing 'name' field")
        if 'description' not in frontmatter:
            self.errors.append("Frontmatter missing 'description' field")

        # Check name format
        if 'name' in frontmatter:
            name = frontmatter['name']
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"Invalid name format: {name}. Use lowercase with hyphens only")

        # Check description contains trigger phrases
        if 'description' in frontmatter:
            desc = frontmatter['description']
            if len(desc) < 50:
                self.warnings.append("Description is very short, consider adding more trigger phrases")

        # Check content after frontmatter
        content_after_frontmatter = content[frontmatter_match.end():].strip()
        if not content_after_frontmatter:
            self.errors.append("SKILL.md has no content after frontmatter")

        self.passed.append("SKILL.md frontmatter and structure valid")

    def _check_naming(self) -> None:
        """Check path and file naming conventions"""
        # Check skill folder name
        folder_name = self.skill_path.name
        if not re.match(r'^[a-z0-9-]+$', folder_name):
            self.errors.append(f"Invalid folder name: {folder_name}. Use lowercase with hyphens only")

        # Check all files have valid names
        for file_path in self.skill_path.rglob('*'):
            if file_path.is_file():
                file_name = file_path.name
                if not re.match(r'^[a-zA-Z0-9_.-]+$', file_name):
                    self.errors.append(f"Invalid file name: {file_name}")

    def _check_assets(self) -> None:
        """Check for required assets"""
        assets_dir = self.skill_path / 'assets'
        templates_dir = assets_dir / 'templates'

        if templates_dir.exists():
            template_files = list(templates_dir.glob('*.md'))
            if len(template_files) == 0:
                self.warnings.append("No template files found in assets/templates")

    def print_report(self) -> None:
        """Print validation report"""
        print("\n" + "=" * 60)
        print("SKILL VALIDATION REPORT")
        print("=" * 60)

        if self.passed:
            print("\n✅ PASSED:")
            for item in self.passed:
                print(f"   • {item}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for item in self.warnings:
                print(f"   • {item}")

        if self.errors:
            print("\n❌ ERRORS:")
            for item in self.errors:
                print(f"   • {item}")

        print("\n" + "=" * 60)
        if self.errors:
            print(f"VALIDATION FAILED: {len(self.errors)} error(s) found")
        elif self.warnings:
            print(f"VALIDATION PASSED: {len(self.warnings)} warning(s)")
        else:
            print("VALIDATION PASSED: No issues found")
        print("=" * 60)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    validator = SkillValidator(skill_path)
    success = validator.validate()
    validator.print_report()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
