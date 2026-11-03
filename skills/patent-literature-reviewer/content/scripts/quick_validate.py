#!/usr/bin/env python3
"""
Patent Literature Reviewer Skill Validator
Validates skill structure and file integrity
"""

import os
import sys
import json
import re


def validate_frontmatter(file_path: str) -> tuple[bool, str]:
    """Validate SKILL.md frontmatter format"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter exists
    if not content.startswith('---'):
        return False, "Frontmatter must start with '---' at line 1"

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter closing '---' not found"

    # Parse frontmatter content
    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter_str = '\n'.join(frontmatter_lines)

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        pattern = f'{field}:'
        if pattern not in frontmatter_str:
            return False, f"Missing required field: {field}"

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_str, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name_value):
            return False, f"Invalid name format: {name_value}. Must be hyphen-case"

    return True, "Frontmatter validation passed"


def validate_meta_json(meta_path: str) -> tuple[bool, str]:
    """Validate _meta.json file structure"""
    if not os.path.exists(meta_path):
        return False, "_meta.json not found"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # Check required fields
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field: {field}"

    # Validate version format
    version = meta.get('version', '')
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"Invalid version format: {version}. Must be semantic versioning (e.g., 1.0.0)"

    return True, "Meta validation passed"


def validate_structure(skill_dir: str) -> tuple[bool, list]:
    """Validate skill directory structure"""
    errors = []

    # Check required files
    required_files = [
        'SKILL.md',
        '_meta.json'
    ]

    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            errors.append(f"Missing required file: {file}")

    # Check recommended directories
    recommended_dirs = ['scripts', 'references']
    for dir_name in recommended_dirs:
        path = os.path.join(skill_dir, dir_name)
        if os.path.exists(path) and not os.path.isdir(path):
            errors.append(f"{dir_name} should be a directory")

    return len(errors) == 0, errors


def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    print(f"Validating skill at: {skill_dir}")
    print("=" * 50)

    all_passed = True

    # Validate frontmatter
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md):
        passed, msg = validate_frontmatter(skill_md)
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} SKILL.md frontmatter: {msg}")
        all_passed = all_passed and passed
    else:
        print("[FAIL] SKILL.md not found")
        all_passed = False

    # Validate _meta.json
    meta_json = os.path.join(skill_dir, '_meta.json')
    passed, msg = validate_meta_json(meta_json)
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} _meta.json: {msg}")
    all_passed = all_passed and passed

    # Validate directory structure
    passed, errors = validate_structure(skill_dir)
    if passed:
        print("[PASS] Directory structure: Valid")
    else:
        print("[FAIL] Directory structure errors:")
        for error in errors:
            print(f"  - {error}")
        all_passed = False

    print("=" * 50)
    if all_passed:
        print("All validations passed!")
        sys.exit(0)
    else:
        print("Validation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
