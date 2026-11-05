#!/usr/bin/env python3
"""
Quick Validation Script for Skill Quality Gate

Validates skill structure, frontmatter, and content quality.
This script checks all mandatory requirements before packaging.

Usage:
    python quick_validate.py <path_to_skill>
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple


class ValidationResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def add_pass(self, message: str):
        self.passed.append(message)

    def add_fail(self, message: str):
        self.failed.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def is_success(self) -> bool:
        return len(self.failed) == 0

    def print_report(self):
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)

        if self.passed:
            print(f"\n✅ PASSED ({len(self.passed)})")
            for msg in self.passed:
                print(f"  ✓ {msg}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)})")
            for msg in self.warnings:
                print(f"  ⚡ {msg}")

        if self.failed:
            print(f"\n❌ FAILED ({len(self.failed)})")
            for msg in self.failed:
                print(f"  ✗ {msg}")

        print("\n" + "-" * 60)
        if self.is_success():
            print("✅ ALL CHECKS PASSED - Skill is ready for packaging")
        else:
            print("❌ VALIDATION FAILED - Fix issues before packaging")
        print("=" * 60)

        return self.is_success()


def validate_skill_directory(skill_path: Path, result: ValidationResult) -> bool:
    """Check if skill directory exists and has basic structure."""
    if not skill_path.exists():
        result.add_fail(f"Skill directory does not exist: {skill_path}")
        return False

    if not skill_path.is_dir():
        result.add_fail(f"Path is not a directory: {skill_path}")
        return False

    result.add_pass(f"Skill directory exists: {skill_path.name}")
    return True


def validate_meta_json(skill_path: Path, result: ValidationResult) -> bool:
    """Validate _meta.json file."""
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        result.add_fail("_meta.json file is missing")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        result.add_fail(f"_meta.json is not valid JSON: {e}")
        return False

    # Check required fields
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            result.add_fail(f"_meta.json missing required field: {field}")
        else:
            result.add_pass(f"_meta.json has field: {field}")

    # Validate version format (semver)
    if 'version' in meta:
        version_pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(version_pattern, meta['version']):
            result.add_fail(f"Invalid version format: {meta['version']} (expected semver)")
        else:
            result.add_pass(f"Version format is valid: {meta['version']}")

    # Validate id
    if 'id' in meta:
        if not meta['id'] == skill_path.name:
            result.add_warning(f"ID mismatch: meta has '{meta['id']}', folder is '{skill_path.name}'")

    return True


def validate_skill_md(skill_path: Path, result: ValidationResult) -> bool:
    """Validate SKILL.md file structure and frontmatter."""
    skill_md_path = skill_path / "SKILL.md"

    if not skill_md_path.exists():
        result.add_fail("SKILL.md file is missing")
        return False

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with frontmatter delimiter
    if not content.startswith('---'):
        result.add_fail("SKILL.md must start with YAML frontmatter (---)")
        return False
    result.add_pass("SKILL.md starts with frontmatter delimiter")

    # Extract and parse frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        result.add_fail("Cannot parse YAML frontmatter from SKILL.md")
        return False

    frontmatter_text = frontmatter_match.group(1)

    # Check for required frontmatter fields
    required_fields = ['name', 'description']
    for field in required_fields:
        pattern = rf'^{field}:\s*.+$'
        if not re.search(pattern, frontmatter_text, re.MULTILINE):
            result.add_fail(f"Frontmatter missing required field: {field}")
        else:
            result.add_pass(f"Frontmatter has field: {field}")

    # Validate name field
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            result.add_fail(f"Invalid name format: '{name_value}' (use lowercase with hyphens)")
        elif name_value != skill_path.name:
            result.add_warning(f"Name mismatch: frontmatter has '{name_value}', folder is '{skill_path.name}'")
        else:
            result.add_pass(f"Name is valid: {name_value}")

    # Check description field
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            result.add_warning("Description is very short, consider adding more detail")
        else:
            result.add_pass(f"Description length is adequate: {len(desc_value)} chars")

    # Check content after frontmatter
    content_after_fm = content[frontmatter_match.end():].strip()
    if len(content_after_fm) < 100:
        result.add_warning("SKILL.md content after frontmatter is very short")
    else:
        result.add_pass(f"SKILL.md has adequate content: {len(content_after_fm)} chars")

    # Check for markdown headings
    if '#' in content_after_fm:
        result.add_pass("SKILL.md contains markdown headings")

    return True


def validate_directory_structure(skill_path: Path, result: ValidationResult):
    """Check for recommended directories and files."""
    recommended_dirs = ['scripts', 'references', 'assets']
    recommended_files = ['SKILL.md', '_meta.json']

    # Check recommended directories
    for dir_name in recommended_dirs:
        dir_path = skill_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            result.add_pass(f"Recommended directory exists: {dir_name}/")
            # Check if scripts directory has validate/pack scripts
            if dir_name == 'scripts':
                if (dir_path / 'quick_validate.py').exists():
                    result.add_pass("Validation script found: quick_validate.py")
                if (dir_path / 'package_skill.py').exists():
                    result.add_pass("Packaging script found: package_skill.py")
        else:
            result.add_warning(f"Recommended directory missing: {dir_name}/")

    # Ensure no unwanted files in root
    unwanted_patterns = ['__pycache__', '.pyc', '.git', '.DS_Store']
    for item in skill_path.iterdir():
        if item.is_file():
            for pattern in unwanted_patterns:
                if pattern in item.name:
                    result.add_fail(f"Found unwanted file: {item.name}")
                    break


def validate_naming(skill_path: Path, result: ValidationResult):
    """Check naming conventions."""
    name = skill_path.name

    # Check length
    if len(name) > 64:
        result.add_fail(f"Skill name too long: {len(name)} chars (max 64)")
    else:
        result.add_pass(f"Skill name length is valid: {len(name)} chars")

    # Check characters (lowercase, numbers, hyphens only)
    if not re.match(r'^[a-z0-9-]+$', name):
        result.add_fail(f"Invalid characters in name: '{name}' (use lowercase, numbers, hyphens)")
    else:
        result.add_pass("Skill name uses valid characters")


def validate_skill(skill_path: str) -> bool:
    """Main validation function."""
    skill_path = Path(skill_path).resolve()

    print(f"\n🔍 Validating skill: {skill_path.name}")
    print("-" * 40)

    result = ValidationResult()

    # Run all validations
    if not validate_skill_directory(skill_path, result):
        result.print_report()
        return False

    validate_naming(skill_path, result)
    validate_meta_json(skill_path, result)
    validate_skill_md(skill_path, result)
    validate_directory_structure(skill_path, result)

    # Print report and return success status
    return result.print_report()


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <path_to_skill>")
        print("Example: python quick_validate.py ./ued-designer")
        sys.exit(1)

    skill_path = sys.argv[1]
    success = validate_skill(skill_path)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
