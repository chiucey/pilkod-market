#!/usr/bin/env python3
"""Quick validation script for embedded-code-generation-optimizer skill."""

import os
import json
import sys

def validate_frontmatter(skill_md_path):
    """Validate frontmatter format and content."""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter exists and is first
    if not content.startswith('---'):
        return False, "SKILL.md must start with frontmatter"

    frontmatter_end = content.find('---', 3)
    if frontmatter_end == -1:
        return False, "Missing closing --- in frontmatter"

    frontmatter_text = content[3:frontmatter_end].strip()

    # Check required fields
    required_fields = ['name', 'description']
    frontmatter_lines = frontmatter_text.split('\n')
    found_fields = {field: False for field in required_fields}

    for line in frontmatter_lines:
        for field in required_fields:
            if line.strip().startswith(f'{field}:'):
                found_fields[field] = True
                break

    for field in required_fields:
        if not found_fields[field]:
            return False, f"Missing required field: {field}"

    # Validate frontmatter is at start of file
    # Already checked: content.startswith('---') at line 14
    # Already checked: closing --- exists at line 18
    # Already checked: required fields present at lines 34-36
    # Frontmatter is valid if we reach here

    return True, "Frontmatter valid"

def validate_meta_json(meta_path):
    """Validate _meta.json exists and has required fields."""
    if not os.path.exists(meta_path):
        return False, "_meta.json not found"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field: {field}"

    if not isinstance(meta['id'], int):
        return False, "id must be an integer"

    if not isinstance(meta['version'], str):
        return False, "version must be a string"

    return True, "_meta.json valid"

def validate_naming(skill_dir):
    """Validate folder and file naming conventions."""
    # Check folder name is hyphen-case
    folder_name = os.path.basename(skill_dir)
    if not folder_name.replace('-', '').isalnum():
        return False, "Folder name must be hyphen-case (English only)"

    # Check SKILL.md name matches folder
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md):
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            frontmatter_end = content.find('---', 3)
            frontmatter = content[3:frontmatter_end].strip()

            for line in frontmatter.split('\n'):
                if line.startswith('name:'):
                    name = line.split(':', 1)[1].strip()
                    if name != folder_name:
                        return False, f"SKILL.md name '{name}' must match folder '{folder_name}'"

    return True, "Naming valid"

def main():
    skill_dir = '/workspace/temp-skills/embedded-code-generation-optimizer'
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    meta_json = os.path.join(skill_dir, '_meta.json')

    all_passed = True

    # Run validations
    checks = [
        ("Frontmatter & Structure", validate_frontmatter, skill_md),
        ("Meta JSON", validate_meta_json, meta_json),
        ("Naming Conventions", validate_naming, skill_dir),
    ]

    for check_name, validator, path in checks:
        passed, message = validator(path)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {check_name}: {message}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nAll validations passed!")
        return 0
    else:
        print("\nValidation failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
