#!/usr/bin/env python3
"""
Quick validation script for OpenClaw Model Selector skill
Validates structure, frontmatter, and key files
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path: str) -> tuple[bool, str]:
    """Validate SKILL.md frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter exists
    if not content.startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter not closed with ---"

    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # Check required fields
    if 'name:' not in frontmatter_text:
        return False, "Frontmatter must contain 'name:' field"

    if 'description:' not in frontmatter_text:
        return False, "Frontmatter must contain 'description:' field"

    # Extract name
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        # Validate name format (hyphen-case)
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
            return False, f"Name '{name}' should be hyphen-case (e.g., 'my-skill')"

        # Validate name length
        if len(name) > 64:
            return False, f"Name '{name}' exceeds 64 characters"

    # Check no markdown title before frontmatter
    for line in lines[:frontmatter_end]:
        if line.startswith('#'):
            return False, "No markdown title (#) should appear before frontmatter"

    return True, "Frontmatter validation passed"


def validate_meta_json(meta_path: str) -> tuple[bool, str]:
    """Validate _meta.json structure"""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json is not valid JSON: {e}"
    except FileNotFoundError:
        return False, "_meta.json not found"

    # Check required fields
    if 'id' not in meta:
        return False, "_meta.json must contain 'id' field"

    if 'version' not in meta:
        return False, "_meta.json must contain 'version' field"

    # Validate ID format (should be a number string)
    if not isinstance(meta['id'], (int, str)):
        return False, "'id' should be a number or string"

    # Validate version format (semver)
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"Version '{version}' should follow semver format (e.g., '1.0.0')"

    return True, "_meta.json validation passed"


def validate_directory_structure(skill_dir: str) -> tuple[bool, list]:
    """Validate directory structure"""
    errors = []
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            errors.append(f"Missing required file: {file}")

    # Check for scripts directory
    scripts_dir = os.path.join(skill_dir, 'scripts')
    if os.path.exists(scripts_dir):
        scripts = os.listdir(scripts_dir)
        if not any(f.endswith('.py') for f in scripts):
            errors.append("scripts/ directory exists but contains no Python files")

    return len(errors) == 0, errors


def validate_skill_name(skill_dir: str, frontmatter_name: str) -> tuple[bool, str]:
    """Validate skill name consistency"""
    dir_name = os.path.basename(os.path.normpath(skill_dir))

    if dir_name != frontmatter_name:
        return False, f"Directory name '{dir_name}' should match frontmatter name '{frontmatter_name}'"

    return True, "Skill name validation passed"


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    print("=" * 60)
    print("OpenClaw Model Selector - Validation Report")
    print("=" * 60)
    print()

    all_passed = True

    # Validate frontmatter
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    passed, msg = validate_frontmatter(skill_md)
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"Frontmatter: {status}")
    print(f"  {msg}")
    if not passed:
        all_passed = False

    # Extract name for further validation
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    frontmatter_name = name_match.group(1).strip() if name_match else ""

    # Validate meta.json
    meta_json = os.path.join(skill_dir, '_meta.json')
    passed, msg = validate_meta_json(meta_json)
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n_meta.json: {status}")
    print(f"  {msg}")
    if not passed:
        all_passed = False

    # Validate directory structure
    passed, errors = validate_directory_structure(skill_dir)
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\nDirectory Structure: {status}")
    for error in errors:
        print(f"  - {error}")
        all_passed = False

    # Validate name consistency
    if frontmatter_name:
        passed, msg = validate_skill_name(skill_dir, frontmatter_name)
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\nName Consistency: {status}")
        print(f"  {msg}")
        if not passed:
            all_passed = False

    print()
    print("=" * 60)
    if all_passed:
        print("✓ All validations passed!")
        return 0
    else:
        print("✗ Some validations failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
