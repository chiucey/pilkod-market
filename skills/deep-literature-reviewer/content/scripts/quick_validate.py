#!/usr/bin/env python3
"""
Quick Validation Script for Deep Literature Reviewer Skill
Validates SKILL.md frontmatter, _meta.json, and directory structure.
"""

import json
import os
import re
import sys
from pathlib import Path

ERRORS = []
WARNINGS = []


def validate_frontmatter(skill_md_path: str) -> bool:
    """Validate SKILL.md frontmatter format."""
    global ERRORS, WARNINGS

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        ERRORS.append("SKILL.md must start with --- (frontmatter delimiter)")
        return False

    lines = content.split('\n')
    frontmatter = {}
    in_frontmatter = False

    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter and ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    if 'name' not in frontmatter:
        ERRORS.append("Frontmatter missing required field: 'name'")

    if 'description' not in frontmatter:
        ERRORS.append("Frontmatter missing required field: 'description'")

    if 'name' in frontmatter:
        name = frontmatter['name']
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            ERRORS.append(f"Skill name '{name}' should use hyphen-case format")

    if 'description' in frontmatter:
        desc = frontmatter['description']
        trigger_keywords = ['调研', '文献', 'research', 'literature', '学术']
        if not any(kw.lower() in desc.lower() for kw in trigger_keywords):
            WARNINGS.append("Description should contain trigger keywords")

    return len(ERRORS) == 0


def validate_meta_json(meta_path: str) -> bool:
    """Validate _meta.json format."""
    global ERRORS, WARNINGS

    if not os.path.exists(meta_path):
        ERRORS.append("_meta.json not found")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        ERRORS.append(f"_meta.json is not valid JSON: {e}")
        return False

    required_fields = ['id', 'name', 'version', 'description']
    for field in required_fields:
        if field not in meta:
            ERRORS.append(f"_meta.json missing required field: '{field}'")

    if 'id' in meta and not isinstance(meta['id'], int):
        ERRORS.append("_meta.json 'id' must be an integer")

    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            ERRORS.append(f"_meta.json 'version' should follow semantic versioning, got: '{version}'")

    return len(ERRORS) == 0


def validate_directory_structure(base_path: str) -> bool:
    """Validate skill directory structure."""
    global ERRORS, WARNINGS

    required_files = ['SKILL.md', '_meta.json']
    for fname in required_files:
        if not os.path.exists(os.path.join(base_path, fname)):
            ERRORS.append(f"Required file missing: {fname}")

    for dname in ['scripts', 'references', 'templates']:
        dpath = os.path.join(base_path, dname)
        if os.path.exists(dpath) and not os.path.isdir(dpath):
            ERRORS.append(f"{dname} should be a directory")

    return len(ERRORS) == 0


def main():
    """Main validation entry point."""
    global ERRORS, WARNINGS

    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    print(f"Validating skill at: {os.path.abspath(skill_dir)}")
    print("-" * 50)

    all_passed = True

    print("Checking frontmatter...")
    if not validate_frontmatter(os.path.join(skill_dir, 'SKILL.md')):
        all_passed = False

    print("Checking _meta.json...")
    if not validate_meta_json(os.path.join(skill_dir, '_meta.json')):
        all_passed = False

    print("Checking directory structure...")
    if not validate_directory_structure(skill_dir):
        all_passed = False

    print("-" * 50)

    if ERRORS:
        print(f"\n❌ ERRORS ({len(ERRORS)}):")
        for e in ERRORS:
            print(f"  - {e}")

    if WARNINGS:
        print(f"\n⚠️  WARNINGS ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"  - {w}")

    if all_passed:
        print("\n✅ All validations passed!")
        return 0
    else:
        print("\n❌ Validation failed. Please fix errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
