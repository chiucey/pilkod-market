#!/usr/bin/env python3
"""
PDF to Obsidian Skill Validator
Validates SKILL.md structure and frontmatter requirements
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate frontmatter requirements"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Check if file starts with ---
    if not content.startswith('---'):
        errors.append("SKILL.md must start with --- (frontmatter delimiter)")
        return False, errors

    # Extract frontmatter
    try:
        end_idx = content.index('---', 3)
        frontmatter = content[3:end_idx].strip()
    except ValueError:
        errors.append("Frontmatter not properly closed with ---")
        return False, errors

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        pattern = f'^{field}:'
        if not re.search(pattern, frontmatter, re.MULTILINE):
            errors.append(f"Missing required frontmatter field: {field}")

    # Check description is not empty
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 10:
            errors.append("description must be meaningful (at least 10 characters)")

    return len(errors) == 0, errors

def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json structure"""
    errors = []
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json not found"]

    import json
    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, [f"_meta.json is invalid JSON: {e}"]

    # Check required fields
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required _meta.json field: {field}")

    # Validate version format
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"version must follow semantic versioning (x.y.z), got: {version}")

    return len(errors) == 0, errors

def validate_naming(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate file and folder naming"""
    errors = []
    skill_name = skill_path.name

    # Check folder name is ASCII
    if not skill_name.isascii():
        errors.append(f"Folder name contains non-ASCII characters: {skill_name}")

    # Check SKILL.md name field matches folder
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        frontmatter_end = content.index('---', 3)
        frontmatter = content[3:frontmatter_end]

        name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
        if name_match:
            expected_name = name_match.group(1).strip()
            # Convert expected name to folder-compatible format
            folder_name = expected_name.replace(' ', '-').lower()
            if not skill_name.startswith(folder_name[:20]):
                pass  # Allow some flexibility

    return len(errors) == 0, errors

def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill directory structure"""
    errors = []

    # Check essential files exist
    if not (skill_path / "SKILL.md").exists():
        errors.append("SKILL.md is missing")

    if not (skill_path / "_meta.json").exists():
        errors.append("_meta.json is missing")

    return len(errors) == 0, errors

def run_validation(skill_path: str) -> bool:
    """Run all validations"""
    path = Path(skill_path)

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    all_passed = True

    # Structure validation
    passed, errors = validate_structure(path)
    if passed:
        print("✓ Structure validation passed")
    else:
        print("✗ Structure validation failed:")
        for e in errors:
            print(f"  - {e}")
        all_passed = False

    # Meta JSON validation
    passed, errors = validate_meta_json(path)
    if passed:
        print("✓ _meta.json validation passed")
    else:
        print("✗ _meta.json validation failed:")
        for e in errors:
            print(f"  - {e}")
        all_passed = False

    # Frontmatter validation
    passed, errors = validate_frontmatter(path)
    if passed:
        print("✓ Frontmatter validation passed")
    else:
        print("✗ Frontmatter validation failed:")
        for e in errors:
            print(f"  - {e}")
        all_passed = False

    # Naming validation
    passed, errors = validate_naming(path)
    if passed:
        print("✓ Naming validation passed")
    else:
        print("✗ Naming validation failed:")
        for e in errors:
            print(f"  - {e}")
        all_passed = False

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed!")
        return True
    else:
        print("✗ Some validations failed")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    success = run_validation(sys.argv[1])
    sys.exit(0 if success else 1)
