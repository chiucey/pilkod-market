#!/usr/bin/env python3
"""
Skill validation script
Check structure and content of movie-downloader skill
"""

import os
import sys
import json
import re
from pathlib import Path

def validate_frontmatter(skill_md_path: str) -> tuple[bool, str]:
    """Validate SKILL.md frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if starts with ---
    if not content.strip().startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # Extract frontmatter
    parts = content.split('---')
    if len(parts) < 3:
        return False, "SKILL.md frontmatter is incomplete"

    frontmatter = parts[1]

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            return False, f"Missing required field: {field}"

    # Check name format
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not name.replace('-', '').replace('_', '').isalnum():
            return False, "name can only contain letters, numbers, hyphens and underscores"
        if ' ' in name:
            return False, "name cannot contain spaces"

    return True, "Frontmatter validation passed"

def validate_meta_json(meta_path: str) -> tuple[bool, str]:
    """Validate _meta.json"""
    if not os.path.exists(meta_path):
        return False, "_meta.json file does not exist"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # Check required fields
        if 'id' not in meta:
            return False, "_meta.json missing 'id' field"
        if 'version' not in meta:
            return False, "_meta.json missing 'version' field"

        # Validate id is integer
        if not isinstance(meta['id'], int):
            return False, "_meta.json 'id' must be an integer"

        # Validate version format
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            return False, "version must follow semantic versioning (e.g., 1.0.0)"

        return True, "_meta.json validation passed"

    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON parse error: {e}"

def validate_directory_structure(base_path: str) -> tuple[bool, str]:
    """Validate directory structure"""
    required_dirs = ['scripts', 'references', 'assets']
    required_files = ['SKILL.md', '_meta.json']

    for dir_name in required_dirs:
        dir_path = os.path.join(base_path, dir_name)
        if not os.path.isdir(dir_path):
            return False, f"Missing directory: {dir_name}"

    for file_name in required_files:
        file_path = os.path.join(base_path, file_name)
        if not os.path.exists(file_path):
            return False, f"Missing file: {file_name}"

    return True, "Directory structure validation passed"

def main():
    skill_path = "/workspace/temp-skills/movie-downloader"

    print("=" * 50)
    print("movie-downloader Skill Validation")
    print("=" * 50)

    all_passed = True

    # Validate directory structure
    passed, msg = validate_directory_structure(skill_path)
    print(f"\n[{'OK' if passed else 'FAIL'}] Directory Structure: {msg}")
    if not passed:
        all_passed = False

    # Validate frontmatter
    passed, msg = validate_frontmatter(os.path.join(skill_path, "SKILL.md"))
    print(f"[{'OK' if passed else 'FAIL'}] Frontmatter: {msg}")
    if not passed:
        all_passed = False

    # Validate _meta.json
    passed, msg = validate_meta_json(os.path.join(skill_path, "_meta.json"))
    print(f"[{'OK' if passed else 'FAIL'}] _meta.json: {msg}")
    if not passed:
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("All validations passed!")
        return 0
    else:
        print("Validation failed, please fix the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
