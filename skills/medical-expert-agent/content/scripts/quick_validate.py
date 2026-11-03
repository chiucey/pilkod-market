#!/usr/bin/env python3
"""
Medical Expert Agent - Quick Validation Script
医疗专家Agent - 快速验证脚本
"""

import os
import json
import re
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def validate_frontmatter(skill_md_path):
    """Validate SKILL.md frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with ---
    if not content.startswith('---'):
        print_error("SKILL.md must start with YAML frontmatter (---)")
        return False

    # Extract frontmatter
    frontmatter_end = content.find('---', 3)
    if frontmatter_end == -1:
        print_error("Missing closing --- for frontmatter")
        return False

    frontmatter = content[3:frontmatter_end].strip()

    # Check required fields
    has_name = 'name:' in frontmatter
    has_description = 'description:' in frontmatter

    if not has_name:
        print_error("Frontmatter missing 'name' field")
        return False

    if not has_description:
        print_error("Frontmatter missing 'description' field")
        return False

    # Extract name value
    name_match = re.search(r'name:\s*(.+)', frontmatter)
    if name_match:
        name = name_match.group(1).strip()
        if ' ' in name:
            print_warning(f"name should use hyphen-case: '{name}'")
        print_success(f"Frontmatter 'name': {name}")

    # Extract description
    desc_match = re.search(r'description:\s*(.+)', frontmatter)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            print_warning("description is too short, should be descriptive")
        else:
            print_success(f"Frontmatter 'description': {desc[:50]}...")

    return True

def validate_meta_json(meta_path):
    """Validate _meta.json structure"""
    if not os.path.exists(meta_path):
        print_error("_meta.json not found")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # Check required fields
        if 'id' not in meta:
            print_error("_meta.json missing 'id' field")
            return False
        print_success(f"_meta.json 'id': {meta['id']}")

        if 'version' not in meta:
            print_error("_meta.json missing 'version' field")
            return False
        print_success(f"_meta.json 'version': {meta['version']}")

        return True
    except json.JSONDecodeError as e:
        print_error(f"_meta.json is not valid JSON: {e}")
        return False

def validate_naming(skill_dir, skill_name):
    """Validate folder and file naming"""
    dir_name = os.path.basename(skill_dir)

    # Check directory name matches frontmatter name
    if dir_name != skill_name:
        print_error(f"Directory name '{dir_name}' should match skill name '{skill_name}'")
        return False

    print_success(f"Directory name matches: {dir_name}")

    # Check for non-ASCII characters in path
    for root, dirs, files in os.walk(skill_dir):
        for d in dirs:
            if not all(ord(c) < 128 for c in d):
                print_error(f"Non-ASCII directory: {os.path.join(root, d)}")
                return False
        for f in files:
            if not all(ord(c) < 128 for c in f):
                print_error(f"Non-ASCII file: {os.path.join(root, f)}")
                return False

    print_success("All file/directory names are ASCII")
    return True

def validate_structure(skill_dir):
    """Validate skill directory structure"""
    required_files = ['SKILL.md', '_meta.json']

    for f in required_files:
        path = os.path.join(skill_dir, f)
        if not os.path.exists(path):
            print_error(f"Missing required file: {f}")
            return False
        print_success(f"Found: {f}")

    # Check for recommended directories
    recommended_dirs = ['references', 'scripts']
    for d in recommended_dirs:
        path = os.path.join(skill_dir, d)
        if os.path.exists(path):
            print_success(f"Found optional directory: {d}")

    return True

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    print("=" * 50)
    print("Medical Expert Agent - Validation Report")
    print("=" * 50)
    print()

    all_passed = True

    # Check structure
    print("[1] Checking directory structure...")
    if not validate_structure(skill_dir):
        all_passed = False

    print()

    # Check frontmatter
    print("[2] Checking SKILL.md frontmatter...")
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if not validate_frontmatter(skill_md):
        all_passed = False

    print()

    # Check meta.json
    print("[3] Checking _meta.json...")
    meta_json = os.path.join(skill_dir, '_meta.json')
    if not validate_meta_json(meta_json):
        all_passed = False

    print()

    # Extract skill name for naming validation
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
    frontmatter_end = content.find('---', 3)
    frontmatter = content[3:frontmatter_end]
    name_match = re.search(r'name:\s*(.+)', frontmatter)
    skill_name = name_match.group(1).strip() if name_match else ""

    # Check naming
    print("[4] Checking naming conventions...")
    if not validate_naming(skill_dir, skill_name):
        all_passed = False

    print()
    print("=" * 50)

    if all_passed:
        print_success("All validation checks passed!")
        return 0
    else:
        print_error("Some validation checks failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
