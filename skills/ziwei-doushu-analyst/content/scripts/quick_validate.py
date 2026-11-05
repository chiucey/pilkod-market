#!/usr/bin/env python3
"""
Quick validation script for ziwei-doushu-analyst skill.
Validates frontmatter, structure, and naming conventions.
"""

import os
import re
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """Validate that SKILL.md has proper frontmatter at the very beginning."""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with ---
    if not content.strip().startswith('---'):
        return False, "SKILL.md must start with --- (frontmatter delimiter)"

    # Check frontmatter structure
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "Frontmatter not properly formatted"

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    if 'name:' not in frontmatter:
        return False, "Frontmatter missing 'name' field"

    if 'description:' not in frontmatter:
        return False, "Frontmatter missing 'description' field"

    # Extract name value
    name_match = re.search(r'name:\s*(.+)', frontmatter)
    if name_match:
        name_value = name_match.group(1).strip()
        if not name_value:
            return False, "name field cannot be empty"
        if ' ' in name_value:
            return False, "name must use hyphen-case (no spaces)"
        if not re.match(r'^[a-z0-9-]+$', name_value):
            return False, "name can only contain lowercase letters, numbers, and hyphens"

    return True, "Frontmatter validation passed"

def validate_meta_json(meta_path):
    """Validate that _meta.json exists and has required fields."""
    if not os.path.exists(meta_path):
        return False, "_meta.json not found"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            return False, "_meta.json missing 'id' field"

        if 'version' not in meta:
            return False, "_meta.json missing 'version' field"

        return True, "_meta.json validation passed"
    except json.JSONDecodeError:
        return False, "_meta.json is not valid JSON"

def validate_directory_structure(skill_dir):
    """Validate the skill directory structure."""
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            return False, f"Required file '{file}' not found"

    return True, "Directory structure validation passed"

def validate_name_consistency(skill_dir, skill_md_path):
    """Validate that folder name matches the name in frontmatter."""
    folder_name = os.path.basename(skill_dir)

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    name_match = re.search(r'name:\s*(.+)', content)
    if name_match:
        frontmatter_name = name_match.group(1).strip()
        if folder_name != frontmatter_name:
            return False, f"Folder name '{folder_name}' does not match frontmatter name '{frontmatter_name}'"

    return True, "Name consistency validation passed"

def main():
    skill_dir = "/workspace/temp-skills/ziwei-doushu-analyst"
    skill_md = os.path.join(skill_dir, "SKILL.md")
    meta_json = os.path.join(skill_dir, "_meta.json")

    print("=" * 50)
    print("Validating ziwei-doushu-analyst skill...")
    print("=" * 50)

    all_passed = True

    # Run validations
    validations = [
        ("Directory Structure", lambda: validate_directory_structure(skill_dir)),
        ("Frontmatter", lambda: validate_frontmatter(skill_md)),
        ("_meta.json", lambda: validate_meta_json(meta_json)),
        ("Name Consistency", lambda: validate_name_consistency(skill_dir, skill_md)),
    ]

    for name, validator in validations:
        passed, message = validator()
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status}: {name}")
        print(f"  {message}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("All validations passed!")
        return 0
    else:
        print("Some validations failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())