#!/usr/bin/env python3
"""
Fundamental Analyst Skill Validation Script
Validates SKILL.md format and content completeness
"""

import os
import re
import json
import yaml
from pathlib import Path

def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """Validate frontmatter format"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md file not found"]

    content = skill_md.read_text(encoding='utf-8')

    # Check if starts with ---
    if not content.strip().startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Cannot parse YAML frontmatter")
        return False, errors

    try:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
    except Exception as e:
        errors.append(f"YAML format error: {e}")
        return False, errors

    # Check required fields
    if 'name' not in frontmatter:
        errors.append("frontmatter missing 'name' field")
    if 'description' not in frontmatter:
        errors.append("frontmatter missing 'description' field")

    # Check name format
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name '{name}' must contain only lowercase letters, numbers, and hyphens")
        if ' ' in name:
            errors.append(f"name '{name}' cannot contain spaces")

    return len(errors) == 0, errors

def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """Validate _meta.json format"""
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json file not found"]

    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return False, ["_meta.json JSON format error"]

    if 'id' not in meta:
        errors.append("_meta.json missing 'id' field")
    if 'version' not in meta:
        errors.append("_meta.json missing 'version' field")

    if 'id' in meta and not isinstance(meta['id'], int):
        errors.append("'id' must be an integer")

    if 'version' in meta and not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        errors.append("'version' must follow semantic versioning (e.g., 1.0.0)")

    return len(errors) == 0, errors

def validate_skill_content(skill_path: str) -> tuple[bool, list[str]]:
    """Validate skill content completeness"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    content = skill_md.read_text(encoding='utf-8')

    # Check required workflow sections
    required_sections = [
        ('Core Capabilities', 'Missing Core Capabilities section'),
        ('Workflow', 'Missing Workflow section'),
        ('Output Format', 'Missing Output Format section'),
        ('Financial Data', 'Missing data acquisition instructions'),
        ('CAN SLIM', 'Missing CAN SLIM analysis'),
    ]

    for section, error_msg in required_sections:
        if section not in content:
            errors.append(error_msg)

    # Check required API interfaces
    required_apis = ['income', 'balancesheet', 'fina_indicator', 'daily_basic']
    for api in required_apis:
        if api not in content:
            errors.append(f"Missing API documentation: {api}")

    return len(errors) == 0, errors

def main():
    import sys

    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    all_passed = True
    results = []

    # Validate frontmatter
    passed, errors = validate_frontmatter(skill_path)
    results.append(("Frontmatter Validation", passed, errors))
    all_passed &= passed

    # Validate _meta.json
    passed, errors = validate_meta_json(skill_path)
    results.append(("_meta.json Validation", passed, errors))
    all_passed &= passed

    # Validate content completeness
    passed, errors = validate_skill_content(skill_path)
    results.append(("Content Completeness Validation", passed, errors))
    all_passed &= passed

    # Output results
    print("=" * 50)
    print("Fundamental Analyst Skill Validation Results")
    print("=" * 50)

    for name, passed, errors in results:
        status = "PASS" if passed else "FAIL"
        print(f"\n{name}: {status}")
        if errors:
            for error in errors:
                print(f"  - {error}")

    print("\n" + "=" * 50)
    if all_passed:
        print("All validations passed")
        sys.exit(0)
    else:
        print("Some validations failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
