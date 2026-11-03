#!/usr/bin/env python3
"""
Quick Validation Script for Expert Coordination Framework Skill
Validates frontmatter, structure, and naming conventions
"""

import os
import re
import sys
import json
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format and content."""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check if file starts with ---
    if not content.strip().startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    lines = content.split("\n")
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = "\n".join(frontmatter_lines)

    # Check required fields
    if not re.search(r"^name:\s*.+", frontmatter_text, re.MULTILINE):
        errors.append("Missing required 'name' field in frontmatter")

    if not re.search(r"^description:\s*.+", frontmatter_text, re.MULTILINE):
        errors.append("Missing required 'description' field in frontmatter")

    # Extract name value
    name_match = re.search(r"^name:\s*(.+)", frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        # Check name matches folder name
        folder_name = skill_path.name
        if name_value != folder_name:
            errors.append(f"Frontmatter 'name' ({name_value}) must match folder name ({folder_name})")
        # Check name length
        if len(name_value) > 64:
            errors.append(f"Skill name exceeds 64 characters: {len(name_value)}")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json format and required fields."""
    errors = []
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

        if "id" not in meta:
            errors.append("Missing required 'id' field in _meta.json")

        if "version" not in meta:
            errors.append("Missing required 'version' field in _meta.json")
        elif not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
            errors.append("Version must follow semantic versioning (e.g., 1.0.0)")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")

    return len(errors) == 0, errors


def validate_naming(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate folder and file naming conventions."""
    errors = []

    # Check folder name is lowercase with hyphens
    folder_name = skill_path.name
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", folder_name):
        errors.append(f"Folder name '{folder_name}' must be lowercase with hyphens only")

    # Check no Chinese or special characters in paths
    for item in skill_path.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(skill_path)
            if not re.match(r"^[a-zA-Z0-9/_.\-]+$", str(rel_path)):
                errors.append(f"Path contains non-ASCII characters: {rel_path}")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate directory structure."""
    errors = []

    # Check required files exist
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        if not (skill_path / filename).exists():
            errors.append(f"Missing required file: {filename}")

    # Check for unwanted files
    unwanted_patterns = [".DS_Store", "*.pyc", "__pycache__", "*.log"]
    for pattern in unwanted_patterns:
        matches = list(skill_path.rglob(pattern))
        if matches:
            errors.append(f"Found unwanted file pattern: {pattern}")

    return len(errors) == 0, errors


def validate(skill_path: str) -> bool:
    """Run all validations and print results."""
    skill_path = Path(skill_path).resolve()  # Convert to absolute path

    if not skill_path.exists():
        print(f"ERROR: Skill path does not exist: {skill_path}")
        return False

    print(f"\nValidating skill: {skill_path.name}")
    print("=" * 50)

    all_valid = True
    all_errors = []

    validators = [
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta_json),
        ("Naming", validate_naming),
        ("Structure", validate_structure),
    ]

    for name, validator in validators:
        valid, errors = validator(skill_path)
        if valid:
            print(f"✓ {name}: PASSED")
        else:
            print(f"✗ {name}: FAILED")
            for error in errors:
                print(f"  - {error}")
            all_errors.extend(errors)
            all_valid = False

    print("=" * 50)
    if all_valid:
        print("✓ All validations PASSED")
        return True
    else:
        print(f"✗ Validation FAILED with {len(all_errors)} error(s)")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    success = validate(sys.argv[1])
    sys.exit(0 if success else 1)
