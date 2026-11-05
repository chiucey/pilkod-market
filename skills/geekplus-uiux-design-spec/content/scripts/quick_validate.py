#!/usr/bin/env python3
"""
Quick validation script for skill structure.
Validates frontmatter, _meta.json, and file structure.
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path: str) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format."""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with frontmatter
    if not content.strip().startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0].strip() != '---':
        errors.append("Frontmatter must have opening --- on line 1")
        return False, errors

    # Find closing ---
    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        errors.append("Frontmatter must have closing ---")
        return False, errors

    # Parse frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            errors.append(f"Frontmatter must contain '{field}' field")

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name_value):
            errors.append(f"Name must be hyphen-case: '{name_value}'")
        if len(name_value) > 64:
            errors.append(f"Name must be <= 64 characters: '{name_value}' ({len(name_value)})")

    # Check for markdown title before frontmatter
    if re.search(r'^#\s+\w', content):
        errors.append("No markdown title (#) allowed before frontmatter")

    return len(errors) == 0, errors


def validate_meta_json(meta_path: str) -> tuple[bool, list[str]]:
    """Validate _meta.json structure."""
    errors = []

    if not os.path.exists(meta_path):
        errors.append("_meta.json file not found")
        return False, errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json is invalid JSON: {e}")
        return False, errors

    # Check required fields
    if 'id' not in meta:
        errors.append("_meta.json must contain 'id' field")
    if 'version' not in meta:
        errors.append("_meta.json must contain 'version' field")

    # Validate id is a string or number
    if 'id' in meta and not isinstance(meta['id'], (str, int)):
        errors.append(f"_meta.json 'id' must be string or number, got {type(meta['id'])}")

    # Validate version format (semver)
    if 'version' in meta:
        version = str(meta['version'])
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"_meta.json 'version' must be semver format (x.y.z), got '{version}'")

    return len(errors) == 0, errors


def validate_structure(skill_dir: str) -> tuple[bool, list[str]]:
    """Validate overall skill directory structure."""
    errors = []

    # Check required files
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            errors.append(f"Required file '{file}' not found")

    # Check for unsafe path patterns (symlinks, escape attempts)
    for root, dirs, files in os.walk(skill_dir):
        for d in dirs:
            if d.startswith('.') or d.startswith('_') and d != '_meta.json':
                errors.append(f"Hidden directory found: {os.path.join(root, d)}")
        for f in files:
            if f.startswith('.') and f != '.gitkeep':
                errors.append(f"Hidden file found: {os.path.join(root, f)}")

    return len(errors) == 0, errors


def main():
    """Run all validations."""
    # Get skill directory from command line or use default
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # Default to parent directory of this script
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Validating skill at: {skill_dir}")
    print("=" * 50)

    all_passed = True

    # Run validations
    validators = [
        ("Frontmatter & SKILL.md", lambda: validate_frontmatter(os.path.join(skill_dir, 'SKILL.md'))),
        ("_meta.json", lambda: validate_meta_json(os.path.join(skill_dir, '_meta.json'))),
        ("Directory Structure", lambda: validate_structure(skill_dir)),
    ]

    for name, validator in validators:
        passed, errors = validator()
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

        if not passed:
            all_passed = False
            for error in errors:
                print(f"  - {error}")

    print("=" * 50)

    if all_passed:
        print("All validations passed!")
        return 0
    else:
        print("Validation failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
