#!/usr/bin/env python3
"""
Quick validation script for skill structure.
Checks frontmatter, file structure, and naming conventions.
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> list:
    """Validate SKILL.md frontmatter format and content."""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return errors

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter exists at start
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return errors

    # Extract frontmatter
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("Frontmatter closing (---) not found")
        return errors

    frontmatter_text = "\n".join(lines[1:frontmatter_end])

    # Check required fields
    if not re.search(r"^name:", frontmatter_text, re.MULTILINE):
        errors.append("Frontmatter missing 'name' field")

    if not re.search(r"^description:", frontmatter_text, re.MULTILINE):
        errors.append("Frontmatter missing 'description' field")

    # Check name format (hyphen-case)
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name):
            errors.append(f"Name '{name}' should be in hyphen-case (e.g., 'skill-name')")

    return errors


def validate_meta_json(skill_path: Path) -> list:
    """Validate _meta.json exists and has required fields."""
    errors = []
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        errors.append("_meta.json not found")
        return errors

    import json
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json is not valid JSON: {e}")
        return errors

    if "id" not in meta:
        errors.append("_meta.json missing 'id' field")
    elif not isinstance(meta["id"], int):
        errors.append("_meta.json 'id' must be an integer")

    if "version" not in meta:
        errors.append("_meta.json missing 'version' field")
    elif not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
        errors.append("_meta.json 'version' should follow semantic versioning (e.g., '1.0.0')")

    return errors


def validate_directory_structure(skill_path: Path) -> list:
    """Validate directory structure."""
    errors = []

    # Skill folder name should match frontmatter name
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if name_match:
            expected_name = name_match.group(1).strip()
            actual_name = skill_path.name
            if expected_name != actual_name:
                errors.append(f"Folder name '{actual_name}' doesn't match frontmatter name '{expected_name}'")

    return errors


def main():
    skill_path = Path(__file__).parent.parent
    all_errors = []

    all_errors.extend(validate_frontmatter(skill_path))
    all_errors.extend(validate_meta_json(skill_path))
    all_errors.extend(validate_directory_structure(skill_path))

    if all_errors:
        print("❌ Validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ Validation passed!")
        print(f"  - Frontmatter format: OK")
        print(f"  - Required fields: OK")
        print(f"  - Meta file: OK")
        print(f"  - Structure: OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
