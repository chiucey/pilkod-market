#!/usr/bin/env python3
"""
Quick validator for skill structure and frontmatter compliance.
Ensures SKILL.md has correct frontmatter and references exist.
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format and required fields."""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check if file starts with ---
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    frontmatter_end = content.find("---", 3)
    if frontmatter_end == -1:
        errors.append("Frontmatter closing --- not found")
        return False, errors

    frontmatter_text = content[3:frontmatter_end].strip()

    # Check required fields
    if "name:" not in frontmatter_text:
        errors.append("Frontmatter missing 'name' field")
    if "description:" not in frontmatter_text:
        errors.append("Frontmatter missing 'description' field")

    # Parse and validate
    try:
        frontmatter = {}
        for line in frontmatter_text.split("\n"):
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

        # Validate name format (hyphen-case)
        name = frontmatter.get("name", "")
        if name and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', name):
            errors.append(f"Name '{name}' should use hyphen-case format")

        # Validate name matches folder
        folder_name = skill_path.name
        if name != folder_name:
            errors.append(f"Name '{name}' should match folder name '{folder_name}'")

        # Validate description
        desc = frontmatter.get("description", "")
        if desc and len(desc) < 20:
            errors.append("Description should be at least 20 characters")

    except Exception as e:
        errors.append(f"Failed to parse frontmatter: {e}")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json exists and has required fields."""
    errors = []
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

        if "id" not in meta:
            errors.append("_meta.json missing 'id' field")
        if "version" not in meta:
            errors.append("_meta.json missing 'version' field")

        # Validate version format (semver)
        version = meta.get("version", "")
        if version and not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"Version '{version}' should follow semver format (x.y.z)")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")
    except Exception as e:
        errors.append(f"Error reading _meta.json: {e}")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate directory structure and file paths."""
    errors = []

    # Check for unsafe paths (symbolic links, absolute paths)
    for root, dirs, files in os.walk(skill_path):
        for d in dirs:
            dir_path = Path(root) / d
            if dir_path.is_symlink():
                errors.append(f"Symbolic link found: {dir_path}")
        for f in files:
            file_path = Path(root) / f
            if file_path.is_symlink():
                errors.append(f"Symbolic link found: {file_path}")

    # Check references paths are valid
    references_dir = skill_path / "references"
    if references_dir.exists():
        for ref_file in references_dir.iterdir():
            if ref_file.is_file():
                # Verify it's a valid file type
                if ref_file.suffix not in [".md", ".txt", ".json", ".yaml", ".yml"]:
                    errors.append(f"Unusual file type in references: {ref_file.name}")

    return len(errors) == 0, errors


def validate_skill(skill_path: str) -> bool:
    """Run all validations and report results."""
    skill_path = Path(skill_path)

    print(f"Validating skill: {skill_path.name}")
    print("=" * 50)

    all_passed = True

    # Validate frontmatter
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("[PASS] Frontmatter validation")
    else:
        print("[FAIL] Frontmatter validation")
        for e in errors:
            print(f"       - {e}")
        all_passed = False

    # Validate meta.json
    passed, errors = validate_meta_json(skill_path)
    if passed:
        print("[PASS] _meta.json validation")
    else:
        print("[FAIL] _meta.json validation")
        for e in errors:
            print(f"       - {e}")
        all_passed = False

    # Validate structure
    passed, errors = validate_structure(skill_path)
    if passed:
        print("[PASS] Structure validation")
    else:
        print("[FAIL] Structure validation")
        for e in errors:
            print(f"       - {e}")
        all_passed = False

    print("=" * 50)
    if all_passed:
        print("All validations PASSED")
        return True
    else:
        print("Some validations FAILED")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_skill.py <skill_path>")
        sys.exit(1)

    success = validate_skill(sys.argv[1])
    sys.exit(0 if success else 1)
