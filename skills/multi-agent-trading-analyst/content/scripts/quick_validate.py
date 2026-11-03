#!/usr/bin/env python3
"""
Quick Validation Script for Multi-Agent Trading Analyst Skill
Validates SKILL.md frontmatter, structure, and naming conventions.
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path: Path) -> tuple[bool, list[str]]:
    """Validate frontmatter structure and required fields."""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter exists
    if not content.startswith('---'):
        errors.append("SKILL.md must start with frontmatter (---)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    if 'name:' not in frontmatter:
        errors.append("Missing required field: name")

    if 'description:' not in frontmatter:
        errors.append("Missing required field: description")

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(f"Invalid name format '{name}': must be hyphen-case (e.g., my-skill)")

    # Validate description contains trigger phrases
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    if desc_match:
        description = desc_match.group(1).strip()
        if len(description) < 20:
            errors.append("Description too short (minimum 20 characters)")
        if '当用户' not in description and 'When' not in description:
            errors.append("Description should contain trigger phrases (当用户.../When...)")

    # Check for markdown title before frontmatter
    if re.match(r'^#\s+\w.*?\n---', content):
        errors.append("Markdown title (#) cannot appear before frontmatter")

    return len(errors) == 0, errors


def validate_meta_json(meta_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json structure."""
    errors = []

    import json

    if not meta_path.exists():
        errors.append("_meta.json file not found")
        return False, errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")
        return False, errors

    # Check required fields
    if 'id' not in meta:
        errors.append("Missing required field in _meta.json: id")
    elif not isinstance(meta['id'], (int, str)):
        errors.append("Field 'id' must be a string or integer")

    if 'version' not in meta:
        errors.append("Missing required field in _meta.json: version")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta.get('version', '')):
        errors.append("Field 'version' must follow semantic versioning (e.g., 1.0.0)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate directory and file naming."""
    errors = []

    # Check skill directory name matches frontmatter name
    skill_md = skill_dir / 'SKILL.md'
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if name_match:
            expected_name = name_match.group(1).strip()
            actual_name = skill_dir.name
            if expected_name != actual_name:
                errors.append(
                    f"Folder name '{actual_name}' does not match frontmatter name '{expected_name}'"
                )

    # Check for non-ASCII characters in paths
    for item in skill_dir.rglob('*'):
        if not all(ord(c) < 128 for c in str(item)):
            errors.append(f"Non-ASCII characters in path: {item}")

    return len(errors) == 0, errors


def main():
    """Main validation entry point."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / 'SKILL.md'
    meta_json = skill_dir / '_meta.json'

    all_errors = []

    print(f"Validating skill: {skill_dir.name}")
    print("-" * 50)

    # Run all validations
    validations = [
        ("Frontmatter & Structure", validate_frontmatter, skill_md),
        ("Meta JSON", validate_meta_json, meta_json),
        ("Directory Structure", validate_directory_structure, skill_dir),
    ]

    all_passed = True
    for name, validator, path in validations:
        if path.exists():
            passed, errors = validator(path)
            if passed:
                print(f"✓ {name}")
            else:
                print(f"✗ {name}")
                for err in errors:
                    print(f"  - {err}")
                all_errors.extend(errors)
                all_passed = False
        else:
            print(f"✗ {name} - File not found: {path}")
            all_passed = False

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed!")
        return 0
    else:
        print(f"✗ {len(all_errors)} validation error(s) found")
        return 1


if __name__ == '__main__':
    sys.exit(main())
