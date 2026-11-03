#!/usr/bin/env python3
"""
Quick validation script for ascii-chart skill.
Validates SKILL.md structure and _meta.json format.
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter exists at start
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    lines = content.split("\n")
    frontmatter_lines = []
    in_frontmatter = False

    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    # Parse frontmatter
    frontmatter = {}
    for line in frontmatter_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    # Required fields
    if "name" not in frontmatter:
        errors.append("Frontmatter missing 'name' field")
    else:
        name = frontmatter["name"]
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Name '{name}' must be lowercase with hyphens only")
        if len(name) > 64:
            errors.append(f"Name '{name}' exceeds 64 character limit")

    if "description" not in frontmatter:
        errors.append("Frontmatter missing 'description' field")
    else:
        desc = frontmatter["description"]
        if len(desc) < 10:
            errors.append("Description too short (minimum 10 characters)")
        # Check for trigger phrases
        if "when" not in desc.lower() and "ask" not in desc.lower():
            errors.append("Description should include trigger phrases (e.g., 'Use when...')")

    return len(errors) == 0, errors


def validate_meta(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in _meta.json: {e}"]

    # Required fields
    if "id" not in meta:
        errors.append("_meta.json missing 'id' field")
    elif not isinstance(meta["id"], str):
        errors.append("_meta.json 'id' must be string")

    if "version" not in meta:
        errors.append("_meta.json missing 'version' field")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
        errors.append("_meta.json 'version' must follow semantic versioning (e.g., 1.0.0)")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill directory structure"""
    errors = []

    # Check required files
    if not (skill_path / "SKILL.md").exists():
        errors.append("SKILL.md is required")

    if not (skill_path / "_meta.json").exists():
        errors.append("_meta.json is required")

    # Check optional directories
    optional_dirs = ["scripts", "references", "assets"]
    for dir_name in optional_dirs:
        dir_path = skill_path / dir_name
        if dir_path.exists() and not dir_path.is_dir():
            errors.append(f"{dir_name} should be a directory")

    return len(errors) == 0, errors


def validate_naming(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate file and directory naming"""
    errors = []

    # Check folder name matches frontmatter name
    folder_name = skill_path.name
    skill_md = skill_path / "SKILL.md"

    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        if content.startswith("---"):
            lines = content.split("\n")
            for line in lines:
                if line.startswith("name:"):
                    frontmatter_name = line.split(":", 1)[1].strip()
                    if frontmatter_name != folder_name:
                        errors.append(
                            f"Folder name '{folder_name}' should match name in frontmatter '{frontmatter_name}'"
                        )
                    break

    # Check all files use ASCII/latin characters
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            file_path = Path(root) / file
            if not file_path.name.isascii():
                errors.append(f"File '{file}' contains non-ASCII characters")
            if not file_path.suffix.lstrip(".").isascii():
                errors.append(f"File '{file}' has non-ASCII extension")

    return len(errors) == 0, errors


def main():
    """Run all validations"""
    # Get skill path from argument or use default
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        # Look for skill in temp-skills directory
        skill_path = Path("/workspace/temp-skills/ascii-chart")

    print(f"Validating skill at: {skill_path}")
    print("=" * 50)

    all_passed = True
    results = {}

    # Run validations
    validators = [
        ("Frontmatter", validate_frontmatter),
        ("Meta JSON", validate_meta),
        ("Structure", validate_structure),
        ("Naming", validate_naming),
    ]

    for name, validator in validators:
        passed, errors = validator(skill_path)
        results[name] = (passed, errors)

        if passed:
            print(f"✓ {name}: PASS")
        else:
            print(f"✗ {name}: FAIL")
            for error in errors:
                print(f"  - {error}")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("✓ All validations passed!")
        return 0
    else:
        print("✗ Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
