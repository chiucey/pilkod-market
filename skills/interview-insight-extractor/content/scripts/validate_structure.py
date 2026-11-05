#!/usr/bin/env python3
"""
Quick validation script for interview-insight-extractor skill
Validates SKILL.md structure and required fields
"""

import os
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def validate_frontmatter():
    """Validate SKILL.md frontmatter format and required fields"""
    skill_file = os.path.join(SKILL_DIR, "SKILL.md")

    if not os.path.exists(skill_file):
        return False, "SKILL.md not found"

    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter starts at line 1
    if not content.startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter not properly closed with ---"

    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Check required fields
    required_fields = ['name', 'description']
    missing_fields = [f for f in required_fields if f not in frontmatter]

    if missing_fields:
        return False, f"Missing required frontmatter fields: {', '.join(missing_fields)}"

    # Check name matches folder
    folder_name = os.path.basename(SKILL_DIR)
    if frontmatter['name'] != folder_name:
        return False, f"Frontmatter name '{frontmatter['name']}' does not match folder name '{folder_name}'"

    return True, "Frontmatter validation passed"

def validate_meta():
    """Validate _meta.json structure"""
    meta_file = os.path.join(SKILL_DIR, "_meta.json")

    if not os.path.exists(meta_file):
        return False, "_meta.json not found"

    import json
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    missing_fields = [f for f in required_fields if f not in meta]

    if missing_fields:
        return False, f"Missing required _meta.json fields: {', '.join(missing_fields)}"

    return True, "_meta.json validation passed"

def validate_output_structure():
    """Validate that output templates are defined"""
    skill_file = os.path.join(SKILL_DIR, "SKILL.md")

    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    required_sections = [
        '用户目标',
        '痛点',
        '行为模式',
        '机会点',
        '建议动作',
        '原话摘录',
        '受访者编号',
        '置信度',
        '知识库',
        '飞书'
    ]

    missing_sections = [s for s in required_sections if s not in content]

    if missing_sections:
        return False, f"Missing required sections: {', '.join(missing_sections)}"

    return True, "Output structure validation passed"

def main():
    print("=" * 50)
    print("Interview Insight Extractor - Validation")
    print("=" * 50)

    checks = [
        ("Frontmatter Validation", validate_frontmatter),
        ("Meta JSON Validation", validate_meta),
        ("Output Structure Validation", validate_output_structure),
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n[CHECK] {name}...")
        passed, message = check_func()
        if passed:
            print(f"  ✓ PASS: {message}")
        else:
            print(f"  ✗ FAIL: {message}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("All validation checks passed!")
        return 0
    else:
        print("Some validation checks failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
