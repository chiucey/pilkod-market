#!/usr/bin/env python3
"""
Quick validation script for skill quality gates.
Checks frontmatter, structure, and naming conventions.
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
        errors.append("SKILL.md must start with --- (frontmatter delimiter)")
        return False, errors

    # Extract frontmatter
    lines = content.split("\n")

    # Find closing --- (after the opening --- on line 0)
    closing_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_idx = i
            break

    if closing_idx == -1:
        errors.append("Frontmatter missing closing ---")
        return False, errors

    # Parse frontmatter
    frontmatter_lines = lines[1:closing_idx]
    frontmatter = {}
    for line in frontmatter_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    # Check required fields
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required frontmatter field: {field}")

    # Validate name format (hyphen-case, max 64 chars)
    if "name" in frontmatter:
        name = frontmatter["name"]
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            errors.append(f"Name must be hyphen-case: '{name}'")
        if len(name) > 64:
            errors.append(f"Name exceeds 64 character limit: {len(name)}")
        # Check name matches folder
        folder_name = skill_path.name
        if name != folder_name:
            errors.append(f"Name '{name}' does not match folder name '{folder_name}'")

    # Check description is not empty
    if "description" in frontmatter and not frontmatter["description"]:
        errors.append("Description cannot be empty")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json format and required fields."""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        errors.append("_meta.json not found")
        return False, errors

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json is invalid JSON: {e}")
        return False, errors

    # Check required fields
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required field in _meta.json: {field}")

    # Validate id is integer
    if "id" in meta and not isinstance(meta["id"], int):
        errors.append("_meta.json 'id' must be an integer")

    # Validate version format (semantic versioning)
    if "version" in meta:
        version = meta["version"]
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            errors.append(f"Version must be semantic (x.y.z): '{version}'")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate directory structure and path names."""
    errors = []

    # Check for non-ASCII characters in path
    for part in skill_path.parts:
        if not all(ord(c) < 128 for c in part):
            errors.append(f"Path contains non-ASCII characters: {part}")

    # Check skill directory name (should match frontmatter name)
    skill_name = skill_path.name
    if not re.match(r"^[a-z0-9-]+$", skill_name):
        errors.append(f"Skill directory name should be hyphen-case: '{skill_name}'")

    # Check for suspicious files (secrets, credentials)
    suspicious_patterns = [".env", "*.pem", "*.key", "credentials", "secrets"]
    for root, dirs, files in os.walk(skill_path):
        for f in files:
            for pattern in suspicious_patterns:
                if pattern.startswith("*") and f.endswith(pattern[1:]):
                    errors.append(f"Potentially sensitive file found: {f}")
                elif pattern == f:
                    errors.append(f"Potentially sensitive file found: {f}")

    return len(errors) == 0, errors


def main():
    """Run all validations."""
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    all_passed = True

    # Run validations
    validations = [
        ("Frontmatter & Required Fields", validate_frontmatter),
        ("_meta.json Format", validate_meta_json),
        ("Directory Structure & Paths", validate_structure),
    ]

    for name, validator in validations:
        passed, errors = validator(skill_path)
        status = "PASS" if passed else "FAIL"
        print(f"\n[{status}] {name}")

        if errors:
            all_passed = False
            for error in errors:
                print(f"  - {error}")

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed!")
        sys.exit(0)
    else:
        print("✗ Validation failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
