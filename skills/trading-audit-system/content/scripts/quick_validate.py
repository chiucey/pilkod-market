#!/usr/bin/env python3
"""
Quick validation script for skill structure and frontmatter.
Validates:
- SKILL.md exists and has valid frontmatter
- _meta.json exists and has valid id/version
- Folder name matches skill name in frontmatter
- No non-ASCII characters in paths/names
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter."""
    errors = []

    if not skill_md_path.exists():
        return False, ["SKILL.md not found"]

    content = skill_md_path.read_text(encoding='utf-8')

    # Check frontmatter exists at start
    if not content.startswith('---'):
        errors.append("SKILL.md must start with --- (frontmatter delimiter)")
        return False, errors

    # Extract frontmatter - standard YAML frontmatter format:
    # ---
    # name: xxx
    # description: xxx
    # ---
    # markdown content
    lines = content.split('\n')

    # Check minimum lines
    if len(lines) < 4:
        errors.append("Invalid frontmatter structure: too few lines")
        return False, errors

    # Find closing --- delimiter (after line 0)
    closing_delimiter_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            closing_delimiter_idx = i
            break

    if closing_delimiter_idx is None:
        errors.append("Invalid frontmatter structure: missing closing ---")
        return False, errors

    # Parse frontmatter lines (between first --- and closing ---)
    frontmatter = {}
    for line in lines[1:closing_delimiter_idx]:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Check required fields
    required = ['name', 'description']
    for field in required:
        if field not in frontmatter:
            errors.append(f"Missing required frontmatter field: {field}")

    # Check name format (hyphen-case)
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
            errors.append(f"Skill name '{name}' must be hyphen-case (lowercase with hyphens)")

    return len(errors) == 0, errors


def validate_meta(meta_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json."""
    errors = []

    if not meta_path.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in _meta.json: {e}"]

    # Check required fields
    if 'id' not in meta:
        errors.append("Missing required field: id")
    if 'version' not in meta:
        errors.append("Missing required field: version")

    return len(errors) == 0, errors


def validate_path_names(skill_dir: Path) -> tuple[bool, list[str]]:
    """Check for non-ASCII characters in paths and names."""
    errors = []

    # Check folder name
    folder_name = skill_dir.name
    if not folder_name.isascii():
        errors.append(f"Folder name contains non-ASCII characters: {folder_name}")

    # Check all file/dir names
    for item in skill_dir.rglob('*'):
        if not item.name.isascii():
            errors.append(f"Path contains non-ASCII characters: {item.relative_to(skill_dir)}")

    return len(errors) == 0, errors


def validate_name_consistency(skill_dir: Path, skill_md_path: Path) -> tuple[bool, list[str]]:
    """Check that folder name matches skill name in frontmatter."""
    errors = []

    if not skill_md_path.exists():
        return True, []  # Already reported

    content = skill_md_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    for line in lines:
        if line.strip().startswith('name:'):
            frontmatter_name = line.split(':', 1)[1].strip()
            if frontmatter_name != skill_dir.name:
                errors.append(
                    f"Name mismatch: folder is '{skill_dir.name}' but frontmatter has '{frontmatter_name}'"
                )
            break

    return len(errors) == 0, errors


def validate_skill(skill_path: str) -> bool:
    """Main validation entry point."""
    skill_dir = Path(skill_path)
    skill_md = skill_dir / 'SKILL.md'
    meta_json = skill_dir / '_meta.json'

    all_valid = True
    all_errors = []

    # Run all validations
    checks = [
        ("Frontmatter", validate_frontmatter(skill_md)),
        ("_meta.json", validate_meta(meta_json)),
        ("Path names (ASCII)", validate_path_names(skill_dir)),
        ("Name consistency", validate_name_consistency(skill_dir, skill_md)),
    ]

    for check_name, (valid, errors) in checks:
        if valid:
            print(f"✓ {check_name}: PASS")
        else:
            print(f"✗ {check_name}: FAIL")
            all_valid = False
            all_errors.extend(errors)

    if all_errors:
        print("\nErrors found:")
        for err in all_errors:
            print(f"  - {err}")

    return all_valid


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
