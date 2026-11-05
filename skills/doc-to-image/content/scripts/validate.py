#!/usr/bin/env python3
"""
Skill Validation Script
Validates doc-to-image skill structure and format
"""

import os
import sys
import json
import re


def validate_frontmatter(skill_path):
    """Validate SKILL.md frontmatter"""
    errors = []

    skill_md = os.path.join(skill_path, 'SKILL.md')
    if not os.path.exists(skill_md):
        return False, ["SKILL.md not found"]

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if starts with ---
    if not content.strip().startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # Check required fields
    if not re.search(r'^name:', frontmatter_text, re.MULTILINE):
        errors.append("frontmatter missing name field")

    if not re.search(r'^description:', frontmatter_text, re.MULTILINE):
        errors.append("frontmatter missing description field")

    # Validate name format
    name_match = re.search(r'^name:\s*(.+)', frontmatter_lines[0] if frontmatter_lines else '', re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if ' ' in name:
            errors.append("name should use hyphen format (e.g. doc-to-image)")
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append("name can only contain lowercase letters, numbers, and hyphens")

    # Check if frontmatter is followed by markdown heading (skip empty lines)
    remaining = '\n'.join(lines[lines.index('---', 1) + 1:])
    remaining_stripped = remaining.strip()
    if remaining_stripped and not remaining_stripped.startswith('#'):
        for line in remaining.split('\n'):
            if line.strip():
                if line.strip().startswith('#'):
                    errors.append("frontmatter cannot be directly followed by markdown heading")
                break

    return len(errors) == 0, errors


def validate_meta_json(skill_path):
    """Validate _meta.json file"""
    errors = []

    meta_path = os.path.join(skill_path, '_meta.json')
    if not os.path.exists(meta_path):
        return False, ["_meta.json not found"]

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"_meta.json format error: {e}"]

    # Check required fields
    if 'id' not in meta:
        errors.append("_meta.json missing id field")
    elif not isinstance(meta['id'], int):
        errors.append("_meta.json id must be integer")

    if 'version' not in meta:
        errors.append("_meta.json missing version field")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        errors.append("_meta.json version format error (should be x.y.z)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path):
    """Validate directory structure"""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not os.path.exists(os.path.join(skill_path, f)):
            errors.append(f"Missing required file: {f}")

    return len(errors) == 0, errors


def validate_script(skill_path):
    """Validate conversion script"""
    script_path = os.path.join(skill_path, 'scripts', 'doc_to_image.py')
    if os.path.exists(script_path):
        if not os.access(script_path, os.R_OK):
            errors = ["doc_to_image.py not readable"]
        else:
            errors = []
    else:
        errors = []

    return len(errors) == 0, errors


def main():
    skill_path = '/workspace/temp-skills/doc-to-image'

    all_passed = True
    results = {}

    # 1. Directory structure validation
    passed, errors = validate_directory_structure(skill_path)
    results['directory_structure'] = {'passed': passed, 'errors': errors}
    if not passed:
        all_passed = False
        print("[FAIL] Directory structure validation:")
        for e in errors:
            print(f"   - {e}")

    # 2. Frontmatter validation
    passed, errors = validate_frontmatter(skill_path)
    results['frontmatter'] = {'passed': passed, 'errors': errors}
    if not passed:
        all_passed = False
        print("[FAIL] Frontmatter validation:")
        for e in errors:
            print(f"   - {e}")

    # 3. _meta.json validation
    passed, errors = validate_meta_json(skill_path)
    results['meta_json'] = {'passed': passed, 'errors': errors}
    if not passed:
        all_passed = False
        print("[FAIL] _meta.json validation:")
        for e in errors:
            print(f"   - {e}")

    # 4. Script validation
    passed, errors = validate_script(skill_path)
    results['script'] = {'passed': passed, 'errors': errors}
    if not passed:
        all_passed = False
        print("[FAIL] Script validation:")
        for e in errors:
            print(f"   - {e}")

    if all_passed:
        print("[PASS] All validations passed!")

    # Output JSON format results
    print("\nValidation results (JSON):")
    print(json.dumps(results, ensure_ascii=False, indent=2))

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
