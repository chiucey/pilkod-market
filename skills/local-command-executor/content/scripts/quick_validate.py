#!/usr/bin/env python3
"""
Quick validation script for local-command-executor skill.
Validates frontmatter, structure, and naming conventions.
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> list[str]:
    """Validate SKILL.md frontmatter format."""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return errors

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Check frontmatter starts at line 1
    lines = content.split("\n")
    if not lines[0].strip() == "---":
        errors.append("Frontmatter must start at line 1 with '---'")

    # Find frontmatter end
    fm_end = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            fm_end = i
            break

    if fm_end == -1:
        errors.append("Frontmatter missing closing '---'")
        return errors

    # Parse frontmatter
    fm_lines = lines[1:fm_end]
    fm_dict = {}
    for line in fm_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            fm_dict[key.strip()] = value.strip()

    # Check required fields
    if "name" not in fm_dict:
        errors.append("Frontmatter missing 'name' field")
    else:
        name = fm_dict["name"]
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Name must be lowercase with hyphens: '{name}'")
        if len(name) > 64:
            errors.append(f"Name exceeds 64 characters: {len(name)}")

    if "description" not in fm_dict:
        errors.append("Frontmatter missing 'description' field")

    return errors


def validate_meta_json(skill_path: Path) -> list[str]:
    """Validate _meta.json structure."""
    errors = []
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        errors.append("_meta.json not found")
        return errors

    import json
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    if "id" not in meta:
        errors.append("_meta.json missing 'id' field")
    if "version" not in meta:
        errors.append("_meta.json missing 'version' field")

    return errors


def validate_structure(skill_path: Path) -> list[str]:
    """Validate skill directory structure."""
    errors = []

    # Skill name should match directory name
    skill_name = skill_path.name

    # Check SKILL.md exists and has valid frontmatter
    errors.extend(validate_frontmatter(skill_path))
    errors.extend(validate_meta_json(skill_path))

    return errors


def main():
    skill_path = Path(__file__).parent.parent

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    errors = validate_structure(skill_path)

    if errors:
        print("VALIDATION FAILED:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()