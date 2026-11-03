#!/usr/bin/env python3
"""
Quick validation script - Check Suzhou Library search skill structure integrity
"""

import os
import sys
import json
import re

SKILL_DIR = "/workspace/temp-skills/suzhou-library-search"

def check_frontmatter():
    """Check SKILL.md frontmatter format"""
    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    if not os.path.exists(skill_md):
        return False, "SKILL.md not found"

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Check first line is ---
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return False, "SKILL.md must start with --- (not markdown header)"

    # Check frontmatter end marker
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return False, "Missing frontmatter end marker ---"

    frontmatter = content[3:end_idx].strip()

    # Check required fields
    if not re.search(r"^name:\s*.+$", frontmatter, re.MULTILINE):
        return False, "Missing name field"

    if not re.search(r"^description:\s*.+$", frontmatter, re.MULTILINE):
        return False, "Missing description field"

    return True, "Frontmatter validation passed"

def check_meta_json():
    """Check _meta.json format"""
    meta_path = os.path.join(SKILL_DIR, "_meta.json")
    if not os.path.exists(meta_path):
        return False, "_meta.json not found"

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        if "id" not in meta:
            return False, "_meta.json missing id field"

        if "version" not in meta:
            return False, "_meta.json missing version field"

        return True, "_meta.json validation passed"
    except json.JSONDecodeError:
        return False, "_meta.json format error"

def check_directory_structure():
    """Check directory structure"""
    required_dirs = ["references"]
    for dir_name in required_dirs:
        dir_path = os.path.join(SKILL_DIR, dir_name)
        if not os.path.exists(dir_path):
            return False, f"Missing {dir_name} directory"

    return True, "Directory structure validation passed"

def main():
    print("=" * 50)
    print("Suzhou Library Search Skill - Structure Validation")
    print("=" * 50)

    checks = [
        ("Frontmatter Check", check_frontmatter),
        ("_meta.json Check", check_meta_json),
        ("Directory Structure Check", check_directory_structure),
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n[Check] {name}...")
        passed, message = check_func()
        status = "PASS" if passed else "FAIL"
        print(f"  {status} {message}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("All checks passed")
        return 0
    else:
        print("Some checks failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())