#!/usr/bin/env python3
"""
Theos Reverse Engineering Skill Validator
Validates SKILL.md structure, frontmatter completeness, and file integrity
"""

import os
import sys
import json
import re

def validate_frontmatter(skill_dir):
    """Validate frontmatter format and content"""
    skrill_md = os.path.join(skill_dir, "SKILL.md")

    with open(skrill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if first line is ---
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        return False, "SKILL.md must start with --- as frontmatter delimiter"

    # Extract frontmatter block
    fm_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            fm_end = i
            break

    if fm_end == -1:
        return False, "Missing frontmatter end marker ---"

    fm_content = '\n'.join(lines[1:fm_end])

    # Validate required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        pattern = rf'^{field}:\s*.+$'
        if not re.search(pattern, fm_content, re.MULTILINE):
            return False, f"Missing required field: {field}"

    # Validate name format
    name_match = re.search(r'^name:\s*(.+)$', fm_content, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, "name must use hyphen-case with only lowercase letters, numbers, and hyphens"
        if len(name) > 64:
            return False, "name length must not exceed 64 characters"

    return True, "Frontmatter validation passed"

def validate_meta(skill_dir):
    """Validate _meta.json format"""
    meta_path = os.path.join(skill_dir, "_meta.json")

    if not os.path.exists(meta_path):
        return False, "Missing _meta.json file"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError:
        return False, "_meta.json format error"

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field: {field}"

    # Validate version format (semantic versioning)
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, "version must follow semantic versioning format (x.y.z)"

    return True, "_meta.json validation passed"

def validate_structure(skill_dir):
    """Validate directory structure"""
    required_files = ['SKILL.md', '_meta.json']

    for f in required_files:
        if not os.path.exists(os.path.join(skill_dir, f)):
            return False, f"Missing required file: {f}"

    # Check if directory name matches name
    skrill_md = os.path.join(skill_dir, "SKILL.md")
    with open(skrill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if name_match:
        expected_name = name_match.group(1).strip()
        dir_name = os.path.basename(skill_dir)
        if expected_name != dir_name:
            return False, f"Directory name '{dir_name}' does not match name '{expected_name}'"

    return True, "Directory structure validation passed"

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_skill.py <skill_dir>")
        sys.exit(1)

    skill_dir = sys.argv[1]

    validations = [
        ("Structure", validate_structure),
        ("Frontmatter", validate_frontmatter),
        ("Meta", validate_meta),
    ]

    all_passed = True
    for name, validator in validations:
        passed, message = validator(skill_dir)
        status = "[PASS]" if passed else "[FAIL]"
        print(f"[{status}] {name}: {message}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] All validations passed!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()