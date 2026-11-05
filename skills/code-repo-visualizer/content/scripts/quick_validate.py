#!/usr/bin/env python3
"""
Quick validation script for code-repo-visualizer skill.
Validates structure, frontmatter, and naming conventions.
"""

import json
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
FRONTMATTER_PATTERN = r'^---\n(.*?)\n---'
REQUIRED_FRONTMATTER = ['name', 'description']
REQUIRED_META = ['id', 'version']


def validate_frontmatter(skill_md_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format and content."""
    errors = []
    content = skill_md_path.read_text(encoding='utf-8')

    # Check frontmatter exists at start
    if not content.startswith('---'):
        errors.append("SKILL.md must start with frontmatter (---)")
        return False, errors

    # Extract frontmatter
    match = re.match(FRONTMATTER_PATTERN, content, re.DOTALL)
    if not match:
        errors.append("Invalid frontmatter format")
        return False, errors

    # Parse YAML-like frontmatter
    fm_text = match.group(1)
    fm_dict = {}

    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            fm_dict[key.strip()] = value.strip()

    # Check required fields
    for field in REQUIRED_FRONTMATTER:
        if field not in fm_dict:
            errors.append(f"Missing required frontmatter field: {field}")

    # Validate name format (kebab-case)
    if 'name' in fm_dict:
        name = fm_dict['name']
        if not re.match(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$', name):
            errors.append(f"Invalid name format '{name}'. Use kebab-case (e.g., 'my-skill')")

        # Check name matches folder
        expected_name = SKILL_DIR.name
        if name != expected_name:
            errors.append(f"Name '{name}' does not match folder name '{expected_name}'")

    return len(errors) == 0, errors


def validate_meta(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json exists and has required fields."""
    errors = []
    meta_path = skill_dir / '_meta.json'

    if not meta_path.exists():
        errors.append("_meta.json not found")
        return False, errors

    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))

        for field in REQUIRED_META:
            if field not in meta:
                errors.append(f"Missing required _meta.json field: {field}")

        if 'version' in meta:
            if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                errors.append(f"Invalid version format: {meta['version']}. Use semantic versioning (e.g., '1.0.0')")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")

    return len(errors) == 0, errors


def validate_structure(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate skill directory structure."""
    errors = []

    # Required files
    if not (skill_dir / 'SKILL.md').exists():
        errors.append("SKILL.md not found")

    if not (skill_dir / '_meta.json').exists():
        errors.append("_meta.json not found")

    # Optional directories (just check they don't contain dangerous content)
    for subdir in ['scripts', 'references', 'assets']:
        subdir_path = skill_dir / subdir
        if subdir_path.exists():
            if not subdir_path.is_dir():
                errors.append(f"{subdir}/ should be a directory")

    return len(errors) == 0, errors


def main():
    """Run all validations and report results."""
    print(f"Validating skill: {SKILL_DIR.name}")
    print("-" * 50)

    all_valid = True

    # Structure validation
    valid, errors = validate_structure(SKILL_DIR)
    if not valid:
        all_valid = False
        print("❌ Structure validation failed:")
        for err in errors:
            print(f"   - {err}")
    else:
        print("✓ Structure validation passed")

    # Frontmatter validation
    valid, errors = validate_frontmatter(SKILL_DIR / 'SKILL.md')
    if not valid:
        all_valid = False
        print("❌ Frontmatter validation failed:")
        for err in errors:
            print(f"   - {err}")
    else:
        print("✓ Frontmatter validation passed")

    # Meta validation
    valid, errors = validate_meta(SKILL_DIR)
    if not valid:
        all_valid = False
        print("❌ Meta validation failed:")
        for err in errors:
            print(f"   - {err}")
    else:
        print("✓ Meta validation passed")

    print("-" * 50)
    if all_valid:
        print("✅ All validations passed!")
        sys.exit(0)
    else:
        print("❌ Validation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
