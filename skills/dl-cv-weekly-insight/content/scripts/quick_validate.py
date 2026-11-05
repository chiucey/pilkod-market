#!/usr/bin/env python3
"""
Quick validation script for skill structure.
Validates frontmatter, naming conventions, and file structure.
"""

import os
import re
import sys
import json
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format."""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check if file starts with frontmatter
    if not content.strip().startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
        return False, errors

    try:
        import yaml
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
    except ImportError:
        # Fallback: parse manually
        frontmatter = {}
        fm_lines = frontmatter_match.group(1).strip().split("\n")
        for line in fm_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

    # Required fields
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required frontmatter field: {field}")

    # Name validation
    if "name" in frontmatter:
        name = frontmatter["name"]
        if not re.match(r"^[a-z0-9][-a-z0-9]*$", name):
            errors.append(f"Invalid name format '{name}': use lowercase with hyphens")
        if len(name) > 64:
            errors.append(f"Name too long ({len(name)} chars): max 64")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json structure."""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        errors.append("_meta.json not found")
        return False, errors

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")
        return False, errors

    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required _meta.json field: {field}")

    # Version format check (semantic versioning)
    if "version" in meta:
        version = meta["version"]
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            errors.append(f"Invalid version format '{version}': use semantic versioning (x.y.z)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate directory naming and structure."""
    errors = []

    # Check directory name is lowercase and hyphenated
    dir_name = skill_path.name
    if not re.match(r"^[a-z0-9][-a-z0-9]*$", dir_name):
        errors.append(f"Invalid directory name '{dir_name}': use lowercase with hyphens")

    # Check for unwanted files
    unwanted_patterns = [r"\.pyc$", r"__pycache__", r"\.DS_Store", r"Thumbs\.db"]
    for pattern in unwanted_patterns:
        for f in skill_path.rglob("*"):
            if re.search(pattern, str(f)):
                # Ignore in scripts directory
                if "scripts" not in str(f):
                    errors.append(f"Unwanted file found: {f}")

    return len(errors) == 0, errors


def validate_references(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate references directory structure."""
    errors = []
    refs_path = skill_path / "references"

    if refs_path.exists():
        for f in refs_path.rglob("*"):
            if f.is_file():
                # Check for non-ASCII characters in filenames
                if not f.name.isascii():
                    errors.append(f"Non-ASCII filename in references: {f.name}")

    return len(errors) == 0, errors


def validate_skill(skill_path: str) -> bool:
    """Run all validations on a skill directory."""
    skill_path = Path(skill_path)
    all_errors = []

    print(f"Validating skill: {skill_path.name}")
    print("-" * 50)

    # Run all validations
    validators = [
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta_json),
        ("Directory Structure", validate_directory_structure),
        ("References", validate_references),
    ]

    all_passed = True
    for name, validator in validators:
        passed, errors = validator(skill_path)
        if not passed:
            all_passed = False
            print(f"❌ {name}: FAILED")
            for error in errors:
                print(f"   - {error}")
        else:
            print(f"✅ {name}: PASSED")

    print("-" * 50)
    if all_passed:
        print("✅ All validations passed!")
        return True
    else:
        print("❌ Validation failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: validate parent of scripts dir (the skill dir)
        script_path = Path(__file__).resolve()
        skill_path = script_path.parent.parent
    else:
        skill_path = sys.argv[1]

    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
