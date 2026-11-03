#!/usr/bin/env python3
"""Validation script for ai-scientist-v2 skill."""

import os
import json
import sys
import yaml
from pathlib import Path

def validate_frontmatter(skill_path):
    """Validate SKILL.md frontmatter format."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    with open(skill_md, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    parts = content.split('---')
    if len(parts) < 3:
        return False, "Invalid frontmatter format"

    try:
        frontmatter = yaml.safe_load(parts[1])
    except:
        return False, "Invalid YAML in frontmatter"

    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            return False, f"Missing required field: {field}"

    if not frontmatter['description'].startswith('Use when'):
        return False, "description must start with 'Use when' for proper routing"

    return True, "Frontmatter validated"

def validate_meta(skill_path):
    """Validate _meta.json."""
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        return False, "_meta.json not found"

    with open(meta_path, 'r') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field in _meta.json: {field}"

    return True, "_meta.json validated"

def validate_structure(skill_path):
    """Validate skill directory structure."""
    required_dirs = ['scripts', 'references', 'assets']
    for dir_name in required_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    return True, "Structure validated"

def main():
    skill_path = Path(__file__).parent.parent
    all_passed = True

    checks = [
        validate_frontmatter(skill_path),
        validate_meta(skill_path),
        validate_structure(skill_path),
    ]

    for passed, message in checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {message}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n[PASS] All validations passed!")
        sys.exit(0)
    else:
        print("\n[FAIL] Validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
