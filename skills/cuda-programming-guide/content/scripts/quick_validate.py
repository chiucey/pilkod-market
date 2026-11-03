#!/usr/bin/env python3
"""Quick validation script for CUDA Programming Guide skill."""

import os
import sys
import json

SKILL_DIR = "/workspace/temp-skills/cuda-programming-guide"

def check_file_exists(path, name):
    """Check if file exists."""
    full_path = os.path.join(SKILL_DIR, path)
    if os.path.exists(full_path):
        print(f"✓ {name} exists")
        return True
    else:
        print(f"✗ {name} missing at {path}")
        return False

def check_frontmatter():
    """Check SKILL.md frontmatter."""
    skill_path = os.path.join(SKILL_DIR, "SKILL.md")
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter at start
    if not content.startswith('---'):
        print("✗ SKILL.md must start with YAML frontmatter (---)")
        return False

    # Parse frontmatter
    lines = content.split('\n')
    fm_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            fm_end = i
            break

    if fm_end == -1:
        print("✗ Frontmatter not closed with ---")
        return False

    fm_lines = lines[1:fm_end]
    fm_dict = {}
    for line in fm_lines:
        if ':' in line:
            key, val = line.split(':', 1)
            fm_dict[key.strip()] = val.strip()

    # Check required fields
    required = ['name', 'description']
    for field in required:
        if field not in fm_dict:
            print(f"✗ Frontmatter missing required field: {field}")
            return False

    # Check name matches folder
    if fm_dict['name'] != os.path.basename(SKILL_DIR):
        print(f"✗ Name '{fm_dict['name']}' should match folder '{os.path.basename(SKILL_DIR)}'")
        return False

    print("✓ Frontmatter valid")
    return True

def check_meta_json():
    """Check _meta.json exists and is valid."""
    meta_path = os.path.join(SKILL_DIR, "_meta.json")
    try:
        with open(meta_path, 'r') as f:
            meta = json.load(f)

        required = ['id', 'version']
        for field in required:
            if field not in meta:
                print(f"✗ _meta.json missing required field: {field}")
                return False

        print("✓ _meta.json valid")
        return True
    except Exception as e:
        print(f"✗ _meta.json error: {e}")
        return False

def check_references():
    """Check reference files exist."""
    refs_dir = os.path.join(SKILL_DIR, "references")
    if not os.path.exists(refs_dir):
        print("✗ references/ directory missing")
        return False

    ref_files = [
        "advanced-features.md",
        "hardware-specs.md",
        "debugging.md",
        "code-examples.md"
    ]

    all_exist = True
    for rf in ref_files:
        if not check_file_exists(os.path.join("references", rf), f"reference/{rf}"):
            all_exist = False

    return all_exist

def main():
    print("=" * 50)
    print("CUDA Programming Guide Skill Validation")
    print("=" * 50)

    checks = [
        check_file_exists("SKILL.md", "SKILL.md"),
        check_file_exists("_meta.json", "_meta.json"),
        check_frontmatter(),
        check_meta_json(),
        check_references(),
    ]

    print("=" * 50)
    if all(checks):
        print("✓ All validations passed!")
        return 0
    else:
        print("✗ Some validations failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())