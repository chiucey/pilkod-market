#!/usr/bin/env python3
"""
Quick Validation Script for AI Creative Studio Skill
Validates SKILL.md structure and frontmatter compliance
"""

import os
import sys
import re
import json
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate frontmatter format and required fields"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter is at the beginning
    if not content.startswith("---"):
        errors.append("Frontmatter must start at line 1 with '---'")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Could not parse frontmatter block")
        return False, errors

    frontmatter_text = frontmatter_match.group(1)

    # Check required fields
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            errors.append(f"Missing required frontmatter field: {field}")

    # Check name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9][-a-z0-9]*$', name_value):
            errors.append(f"name '{name_value}' should use hyphen-case format")

    # Check description is not empty
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            errors.append("description should be descriptive (at least 20 chars)")
        if "Use when" not in desc_value and "当用户" not in desc_value:
            errors.append("description should contain trigger phrase (e.g., 'Use when...' or '当用户...')")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json structure"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in _meta.json: {e}"]

    # Check required fields
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required field in _meta.json: {field}")

    # Validate version format (semantic versioning)
    if "version" in meta:
        version = meta["version"]
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"version '{version}' should follow semantic versioning (e.g., 1.0.0)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill directory structure"""
    errors = []

    # Check required files
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        if not (skill_path / filename).exists():
            errors.append(f"Missing required file: {filename}")

    # Check optional directories
    optional_dirs = ["scripts", "references", "assets"]
    for dirname in optional_dirs:
        dir_path = skill_path / dirname
        if dir_path.exists() and not dir_path.is_dir():
            errors.append(f"{dirname} should be a directory")

    return len(errors) == 0, errors


def validate_skill_name(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill folder name matches frontmatter name"""
    errors = []

    meta_file = skill_path / "_meta.json"
    skill_md = skill_path / "SKILL.md"

    if not meta_file.exists() or not skill_md.exists():
        return True, []  # Already reported in other validations

    # Get name from frontmatter
    content = skill_md.read_text(encoding="utf-8")
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return True, []

    frontmatter_text = frontmatter_match.group(1)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)

    if name_match:
        frontmatter_name = name_match.group(1).strip()
        folder_name = skill_path.name

        if frontmatter_name != folder_name:
            errors.append(
                f"Skill folder name '{folder_name}' does not match "
                f"frontmatter name '{frontmatter_name}'"
            )

    return len(errors) == 0, errors


def main():
    """Run all validations"""
    # Get skill path from command line or use current directory
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    all_errors = []
    all_passed = True

    # Run all validations
    validations = [
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta_json),
        ("Directory Structure", validate_directory_structure),
        ("Skill Name", validate_skill_name),
    ]

    for name, validator in validations:
        passed, errors = validator(skill_path)
        if passed:
            print(f"✓ {name}: PASSED")
        else:
            print(f"✗ {name}: FAILED")
            for error in errors:
                print(f"  - {error}")
            all_errors.extend(errors)
            all_passed = False

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed!")
        return 0
    else:
        print(f"✗ {len(all_errors)} validation error(s) found")
        return 1


if __name__ == "__main__":
    sys.exit(main())
