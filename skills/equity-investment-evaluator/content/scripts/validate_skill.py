#!/usr/bin/env python3
"""
Quick Validation Script for equity-investment-evaluator skill
Validates frontmatter, structure, and naming conventions
"""

import os
import sys
import json
import re
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
ERRORS = []
WARNINGS = []

def log_error(msg):
    ERRORS.append(f"[ERROR] {msg}")

def log_warning(msg):
    WARNINGS.append(f"[WARN] {msg}")

def check_frontmatter():
    """Validate SKILL.md frontmatter"""
    skill_md = SKILL_ROOT / "SKILL.md"
    if not skill_md.exists():
        log_error("SKILL.md not found")
        return False

    content = skill_md.read_text(encoding='utf-8')

    # Check frontmatter starts at line 1
    if not content.startswith('---'):
        log_error("SKILL.md must start with --- (frontmatter delimiter)")
        return False

    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        log_error("Invalid frontmatter structure")
        return False

    frontmatter = parts[1]

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            log_error(f"Missing required frontmatter field: {field}")

    # Check name matches directory
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        expected_dir = name.replace(' ', '-')
        actual_dir = SKILL_ROOT.name
        if expected_dir != actual_dir:
            log_error(f"Name mismatch: frontmatter='{name}', directory='{actual_dir}'")

    # Check name is English only (hyphen-case)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            log_warning(f"Name should be hyphen-case (a-z, 0-9, -): '{name}'")
        if len(name) > 64:
            log_warning(f"Name exceeds 64 characters: {len(name)}")

    # Check description contains trigger phrases
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if 'Use when' not in desc and '当用户' not in desc:
            log_warning("Description should include trigger phrases (e.g., 'Use when...')")

    return len(ERRORS) == 0

def check_meta_json():
    """Validate _meta.json structure"""
    meta_path = SKILL_ROOT / "_meta.json"
    if not meta_path.exists():
        log_error("_meta.json not found")
        return False

    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON in _meta.json: {e}")
        return False

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            log_error(f"Missing required field in _meta.json: {field}")

    if 'id' in meta and not isinstance(meta['id'], int):
        log_error("Field 'id' in _meta.json must be an integer")

    if 'version' in meta and not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        log_warning(f"Version should follow semantic versioning: {meta.get('version')}")

    return len(ERRORS) == 0

def check_structure():
    """Validate directory structure"""
    required_dirs = []
    recommended_dirs = ['references']

    for dir_name in required_dirs:
        dir_path = SKILL_ROOT / dir_name
        if not dir_path.exists():
            log_error(f"Missing required directory: {dir_name}")

    for dir_name in recommended_dirs:
        dir_path = SKILL_ROOT / dir_name
        if not dir_path.exists():
            log_warning(f"Missing recommended directory: {dir_name}")

    return len(ERRORS) == 0

def check_path_naming():
    """Ensure all paths and names are English only"""
    # Check directory name
    dir_name = SKILL_ROOT.name
    if not re.match(r'^[a-z0-9-]+$', dir_name):
        log_error(f"Directory name should be English only (a-z, 0-9, -): '{dir_name}'")

    # Check all file names
    for file_path in SKILL_ROOT.rglob('*'):
        if file_path.is_file():
            name = file_path.name
            if not re.match(r'^[a-zA-Z0-9_.-]+$', name):
                log_error(f"File name should be English only: '{name}'")

    return len(ERRORS) == 0

def main():
    print("=" * 50)
    print("Skill Validation Report")
    print("=" * 50)
    print(f"Skill: {SKILL_ROOT.name}")
    print()

    all_passed = True

    print("[1] Checking frontmatter...")
    if check_frontmatter():
        print("    PASS")
    else:
        all_passed = False

    print("[2] Checking _meta.json...")
    if check_meta_json():
        print("    PASS")
    else:
        all_passed = False

    print("[3] Checking structure...")
    if check_structure():
        print("    PASS")
    else:
        all_passed = False

    print("[4] Checking path naming...")
    if check_path_naming():
        print("    PASS")
    else:
        all_passed = False

    print()
    print("=" * 50)

    if ERRORS:
        print("ERRORS FOUND:")
        for e in ERRORS:
            print(f"  {e}")
        print()

    if WARNINGS:
        print("WARNINGS:")
        for w in WARNINGS:
            print(f"  {w}")
        print()

    if all_passed:
        print("VALIDATION PASSED - Skill is ready for packaging")
        return 0
    else:
        print("VALIDATION FAILED - Please fix errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
