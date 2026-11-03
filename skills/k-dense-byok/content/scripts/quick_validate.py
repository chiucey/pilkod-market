#!/usr/bin/env python3
"""
K-Dense BYOK Skill Validation Script
Validates the skill structure and frontmatter compliance
"""

import json
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format"""
    errors = []
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    with open(skill_md, 'r') as f:
        content = f.read()

    # Check frontmatter starts at beginning
    if not content.startswith('---'):
        errors.append("SKILL.md must start with '---' (YAML frontmatter delimiter)")
        return False, errors

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False
    frontmatter_end = -1

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                frontmatter_end = i
                break

        if in_frontmatter:
            frontmatter_lines.append(line)

    if frontmatter_end == -1:
        errors.append("Frontmatter not properly closed with '---'")
        return False, errors

    # Check for required fields
    frontmatter_text = '\n'.join(frontmatter_lines)

    if 'name:' not in frontmatter_text:
        errors.append("Frontmatter must contain 'name:' field")

    if 'description:' not in frontmatter_text:
        errors.append("Frontmatter must contain 'description:' field")

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if ' ' in name_value:
            errors.append(f"name should use hyphen-case, found: '{name_value}'")
        if not name_value.replace('-', '').replace('_', '').isalnum():
            errors.append(f"name contains invalid characters: '{name_value}'")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json format"""
    errors = []
    meta_path = skill_path / '_meta.json'

    if not meta_path.exists():
        return False, ["_meta.json not found"]

    try:
        with open(meta_path, 'r') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in _meta.json: {e}"]

    # Check required fields
    if 'id' not in meta:
        errors.append("_meta.json must contain 'id' field")

    if 'version' not in meta:
        errors.append("_meta.json must contain 'version' field")

    # Validate id is a number
    if 'id' in meta:
        try:
            int(meta['id'])
        except (ValueError, TypeError):
            errors.append("'id' must be a valid integer")

    # Validate version format
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append("'version' should follow semantic versioning (e.g., 1.0.0)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill directory structure"""
    errors = []

    # Check folder name matches frontmatter name
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        with open(skill_md, 'r') as f:
            content = f.read()

        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if name_match:
            expected_name = name_match.group(1).strip()
            actual_name = skill_path.name

            # Allow some flexibility (e.g., vscode-name vs vscode_name)
            normalized_expected = expected_name.lower().replace('_', '-')
            normalized_actual = actual_name.lower().replace('_', '-')

            if normalized_expected != normalized_actual:
                errors.append(
                    f"Folder name '{actual_name}' should match frontmatter name '{expected_name}'"
                )

    return len(errors) == 0, errors


def main():
    skill_path = Path(__file__).parent.parent
    all_errors = []
    all_passed = True

    # Run all validations
    validations = [
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta_json),
        ("Directory Structure", validate_directory_structure),
    ]

    for name, validator in validations:
        passed, errors = validator(skill_path)

        if not passed:
            all_passed = False
            print(f"\n✗ {name} validation failed:")
            for error in errors:
                print(f"  - {error}")
                all_errors.append(f"{name}: {error}")
        else:
            print(f"✓ {name} validation passed")

    print()
    if all_passed:
        print("All validations passed! Skill is ready for packaging.")
        return 0
    else:
        print(f"Found {len(all_errors)} error(s). Please fix before packaging.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
