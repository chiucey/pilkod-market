#!/usr/bin/env python3
"""
Quick validation script for edu-ppt-creator skill.
Validates frontmatter structure and required files.
"""

import os
import sys
import json
import re
from pathlib import Path

def validate_frontmatter(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format."""
    errors = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding='utf-8')

    # Check frontmatter is at the start
    if not content.startswith('---'):
        errors.append("SKILL.md must start with --- (frontmatter delimiter)")
        return False, errors

    # Extract frontmatter - lines[0] is first '---'
    lines = content.split('\n')
    if len(lines) < 3:
        errors.append("Invalid frontmatter structure")
        return False, errors

    # Find closing ---
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        errors.append("Frontmatter missing closing ---")
        return False, errors

    frontmatter_text = '\n'.join(lines[1:end_idx+1])

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            errors.append(f"Missing required frontmatter field: {field}")

    # Validate name format (hyphen-case, English only)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name '{name}' must be lowercase with hyphens only (English)")

    # Validate description exists and is not empty
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 10:
            errors.append("description too short (min 10 characters)")

    return len(errors) == 0, errors


def validate_meta_json(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json format."""
    errors = []
    meta_file = skill_dir / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in _meta.json: {e}"]

    # Check required fields
    if 'id' not in meta:
        errors.append("Missing 'id' in _meta.json")
    if 'version' not in meta:
        errors.append("Missing 'version' in _meta.json")

    return len(errors) == 0, errors


def validate_structure(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate directory structure."""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for fname in required_files:
        if not (skill_dir / fname).exists():
            errors.append(f"Missing required file: {fname}")

    return len(errors) == 0, errors


def main():
    skill_dir = Path(__file__).parent.parent

    print(f"Validating skill: {skill_dir.name}")
    print("-" * 50)

    all_valid = True

    # Structure validation
    valid, errors = validate_structure(skill_dir)
    if valid:
        print("[PASS] Structure")
    else:
        print("[FAIL] Structure")
        for e in errors:
            print(f"  - {e}")
        all_valid = False

    # Frontmatter validation
    valid, errors = validate_frontmatter(skill_dir)
    if valid:
        print("[PASS] Frontmatter")
    else:
        print("[FAIL] Frontmatter")
        for e in errors:
            print(f"  - {e}")
        all_valid = False

    # Meta JSON validation
    valid, errors = validate_meta_json(skill_dir)
    if valid:
        print("[PASS] _meta.json")
    else:
        print("[FAIL] _meta.json")
        for e in errors:
            print(f"  - {e}")
        all_valid = False

    print("-" * 50)
    if all_valid:
        print("All validations passed!")
        return 0
    else:
        print("Validation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
