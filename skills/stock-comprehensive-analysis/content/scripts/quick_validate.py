#!/usr/bin/env python3
"""
Quick Validation Script
Validates skill structure and frontmatter without packaging.
"""

import os
import json
import re
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list]:
    """Validate SKILL.md frontmatter format."""
    errors = []
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text()

    # Check frontmatter starts at beginning
    if not content.startswith('---'):
        errors.append("SKILL.md must start with '---' (YAML frontmatter)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Could not parse YAML frontmatter")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    if 'name:' not in frontmatter:
        errors.append("Frontmatter missing 'name:' field")
    if 'description:' not in frontmatter:
        errors.append("Frontmatter missing 'description:' field")

    # Check name matches folder
    folder_name = skill_path.name
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        frontmatter_name = name_match.group(1).strip()
        if frontmatter_name != folder_name:
            errors.append(f"Name mismatch: frontmatter='{frontmatter_name}' vs folder='{folder_name}'")

    return len(errors) == 0, errors

def validate_meta(skill_path: Path) -> tuple[bool, list]:
    """Validate _meta.json structure."""
    errors = []
    meta_file = skill_path / '_meta.json'

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text())

        if 'id' not in meta:
            errors.append("_meta.json missing 'id' field")
        if 'version' not in meta:
            errors.append("_meta.json missing 'version' field")
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    return len(errors) == 0, errors

def main():
    skill_path = Path('/workspace/temp-skills/stock-comprehensive-analysis')

    all_passed = True

    # Check frontmatter
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("✓ SKILL.md frontmatter validation passed")
    else:
        print("✗ SKILL.md frontmatter validation failed:")
        for e in errors:
            print(f"  - {e}")
        all_passed = False

    # Check _meta.json
    passed, errors = validate_meta(skill_path)
    if passed:
        print("✓ _meta.json validation passed")
    else:
        print("✗ _meta.json validation failed:")
        for e in errors:
            print(f"  - {e}")
        all_passed = False

    if all_passed:
        print("\n✓ All validations passed")
        return 0
    else:
        print("\n✗ Validation failed")
        return 1

if __name__ == '__main__':
    exit(main())
