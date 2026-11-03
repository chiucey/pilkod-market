#!/usr/bin/env python3
"""
Skill Validation Script for super-investment-manager
Validates SKILL.md structure and _meta.json
"""

import os
import re
import json
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """Validate SKILL.md frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with frontmatter
    if not content.startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter"

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "Invalid frontmatter format"

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(f'^{field}:', frontmatter, re.MULTILINE):
            return False, f"Missing required frontmatter field: {field}"

    # Check name matches folder
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        folder_name = Path(skill_md_path).parent.name
        if name != folder_name:
            return False, f"name '{name}' does not match folder name '{folder_name}'"

    return True, "Frontmatter validation passed"

def validate_meta_json(meta_path):
    """Validate _meta.json structure"""
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # Check required fields
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required _meta.json field: {field}"

    # Validate ID format
    if not isinstance(meta['id'], (int, str)):
        return False, "id must be a number or string"

    # Validate version format
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, "version must follow semver format (e.g., 1.0.0)"

    return True, "_meta.json validation passed"

def validate_directory_structure(skill_dir):
    """Validate skill directory structure"""
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = skill_dir / filename
        if not filepath.exists():
            return False, f"Missing required file: {filename}"

    return True, "Directory structure validation passed"

def main():
    skill_dir = Path(__file__).parent.parent
    skill_md_path = skill_dir / 'SKILL.md'
    meta_path = skill_dir / '_meta.json'

    print("=" * 60)
    print("Skill Validation Report")
    print("=" * 60)

    all_passed = True

    # Validate directory structure
    print("\n[1/3] Validating directory structure...")
    passed, msg = validate_directory_structure(skill_dir)
    print(f"  {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # Validate frontmatter
    print("\n[2/3] Validating frontmatter...")
    passed, msg = validate_frontmatter(skill_md_path)
    print(f"  {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # Validate _meta.json
    print("\n[3/3] Validating _meta.json...")
    passed, msg = validate_meta_json(meta_path)
    print(f"  {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All validations passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some validations failed. Please fix and retry.")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    exit(main())
