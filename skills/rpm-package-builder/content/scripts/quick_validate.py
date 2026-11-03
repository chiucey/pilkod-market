#!/usr/bin/env python3
"""
RPM Package Builder Skill - Quick Validation Script

This script validates the skill structure and frontmatter compliance.
"""

import os
import sys
import re
import json
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter compliance."""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter at start of file
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid YAML frontmatter format")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    if not re.search(r"^name:", frontmatter, re.MULTILINE):
        errors.append("Missing required field: name")

    if not re.search(r"^description:", frontmatter, re.MULTILINE):
        errors.append("Missing required field: description")

    # Check name format (hyphen-case)
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            errors.append(f"Invalid name format '{name}': use hyphen-case (e.g., 'my-skill')")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json structure."""
    errors = []
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        errors.append("_meta.json not found")
        return False, errors

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

        if "id" not in meta:
            errors.append("_meta.json missing 'id' field")

        if "version" not in meta:
            errors.append("_meta.json missing 'version' field")

        # Validate version format (semantic versioning)
        if "version" in meta:
            version = meta["version"]
            if not re.match(r"^\d+\.\d+\.\d+$", version):
                errors.append(f"Invalid version format '{version}': use semver (e.g., '1.0.0')")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path, skill_name: str) -> tuple[bool, list[str]]:
    """Validate directory structure and naming."""
    errors = []

    # Check skill folder name matches frontmatter name
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if name_match:
            expected_name = name_match.group(1).strip()
            actual_name = skill_path.name
            if expected_name != actual_name:
                errors.append(
                    f"Skill folder name '{actual_name}' does not match "
                    f"frontmatter name '{expected_name}'"
                )

    # Check for forbidden files in wrong locations
    forbidden_patterns = ["node_modules", "__pycache__", ".git"]
    for root, dirs, files in os.walk(skill_path):
        for pattern in forbidden_patterns:
            if pattern in dirs or pattern in files:
                errors.append(f"Forbidden file/directory found: {pattern}")

    return len(errors) == 0, errors


def validate_readme(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate README or documentation exists."""
    warnings = []
    readme = skill_path / "README.md"
    references = skill_path / "references"

    if not readme.exists() and not references.exists():
        warnings.append("No README.md or references/ directory found")

    return len(warnings) == 0, warnings


def main():
    """Main validation entry point."""
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill-path>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])

    if not skill_path.exists():
        print(f"Error: Skill path does not exist: {skill_path}")
        sys.exit(1)

    print(f"Validating skill: {skill_path}")
    print("-" * 50)

    all_passed = True

    # Validate frontmatter
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("[PASS] Frontmatter validation")
    else:
        print("[FAIL] Frontmatter validation")
        for error in errors:
            print(f"  - {error}")
        all_passed = False

    # Validate meta.json
    passed, errors = validate_meta_json(skill_path)
    if passed:
        print("[PASS] _meta.json validation")
    else:
        print("[FAIL] _meta.json validation")
        for error in errors:
            print(f"  - {error}")
        all_passed = False

    # Validate structure
    passed, errors = validate_structure(skill_path, skill_path.name)
    if passed:
        print("[PASS] Directory structure validation")
    else:
        print("[FAIL] Directory structure validation")
        for error in errors:
            print(f"  - {error}")
        all_passed = False

    # Validate README (warnings only)
    passed, warnings = validate_readme(skill_path)
    if passed:
        print("[PASS] Documentation check")
    else:
        print("[WARN] Documentation check")
        for warning in warnings:
            print(f"  - {warning}")

    print("-" * 50)

    if all_passed:
        print("All validation checks passed!")
        sys.exit(0)
    else:
        print("Validation failed. Please fix the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
