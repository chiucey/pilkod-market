#!/usr/bin/env python3
"""
Quick validation script for excel-processor skill.
Validates structure and frontmatter compliance.
"""

import os
import sys
import json
from pathlib import Path


def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """Validate skill structure and return (success, errors)."""
    errors = []
    skill_path = Path(skill_path)

    # Check directory exists
    if not skill_path.exists():
        return False, [f"Skill directory not found: {skill_path}"]

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    # Read and validate frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Parse frontmatter
    try:
        frontmatter_end = content.index('---', 3) + 3
        frontmatter = content[3:frontmatter_end-3].strip()

        required_fields = ['name', 'description']
        for field in required_fields:
            if not any(line.strip().startswith(f'{field}:') for line in frontmatter.split('\n')):
                errors.append(f"Missing required frontmatter field: {field}")
    except ValueError:
        errors.append("Invalid frontmatter format (missing closing ---)")

    # Check _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError:
            errors.append("_meta.json is not valid JSON")

    return len(errors) == 0, errors


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success, errors = validate_skill(skill_path)

    if success:
        print(f"✓ Validation passed for {skill_path}")
        sys.exit(0)
    else:
        print(f"✗ Validation failed for {skill_path}:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
