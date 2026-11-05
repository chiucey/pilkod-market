#!/usr/bin/env python3
"""
Quick validation script for wechat-copywriter skill.
Validates SKILL.md frontmatter, _meta.json, and directory structure.
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format and content."""
    errors = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check if frontmatter is at the very beginning
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        errors.append("Cannot parse YAML frontmatter")
        return False, errors

    frontmatter_text = match.group(1)

    # Parse YAML-like frontmatter
    try:
        fm = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                fm[key.strip()] = value.strip().strip('"\'')
    except Exception as e:
        errors.append(f"Failed to parse frontmatter: {e}")
        return False, errors

    # Check required fields
    if 'name' not in fm:
        errors.append("Frontmatter missing 'name' field")
    else:
        name = fm['name']
        # Validate name format (hyphen-case, <= 64 chars)
        if not re.match(r'^[a-z][a-z0-9-]*$', name):
            errors.append(f"Invalid name format '{name}': use hyphen-case (e.g., 'my-skill')")
        if len(name) > 64:
            errors.append(f"Name '{name}' exceeds 64 characters")
        # Validate name matches directory
        if name != skill_dir.name:
            errors.append(f"Name '{name}' does not match directory '{skill_dir.name}'")

    if 'description' not in fm:
        errors.append("Frontmatter missing 'description' field")
    elif len(fm.get('description', '')) < 10:
        errors.append("Description too short (minimum 10 characters)")

    return len(errors) == 0, errors


def validate_meta_json(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json structure."""
    errors = []
    meta_file = skill_dir / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in _meta.json: {e}"]

    # Check required fields
    if 'id' not in meta:
        errors.append("_meta.json missing 'id' field")
    elif not isinstance(meta['id'], int):
        errors.append("_meta.json 'id' must be an integer")

    if 'version' not in meta:
        errors.append("_meta.json missing 'version' field")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta.get('version', '')):
        errors.append("_meta.json 'version' must follow semantic versioning (e.g., '1.0.0')")

    return len(errors) == 0, errors


def validate_references(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate references directory and referenced files."""
    errors = []
    refs_dir = skill_dir / "references"

    # Check if references directory exists
    if not refs_dir.exists():
        return True, []  # Optional, no error

    # Read SKILL.md to find referenced files
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        # Find references mentioned in SKILL.md
        ref_pattern = r'references/([a-zA-Z0-9_-]+\.md)'
        referenced_files = set(re.findall(ref_pattern, content))

        for ref_file in referenced_files:
            ref_path = refs_dir / ref_file
            if not ref_path.exists():
                errors.append(f"Referenced file '{ref_file}' not found in references/")

    return len(errors) == 0, errors


def validate_no_secrets(skill_dir: Path) -> tuple[bool, list[str]]:
    """Check for potential secrets or sensitive data."""
    errors = []

    dangerous_patterns = [
        (r'password\s*=\s*["\'].*?["\']', 'password'),
        (r'api[_-]?key\s*=\s*["\'].*?["\']', 'api_key'),
        (r'secret\s*=\s*["\'].*?["\']', 'secret'),
        (r'token\s*=\s*["\'].*?["\']', 'token'),
    ]

    for md_file in skill_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for pattern, name in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(f"Potential {name} found in {md_file.relative_to(skill_dir)}")

    return len(errors) == 0, errors


def main():
    """Run all validations."""
    skill_dir = Path(__file__).parent.parent
    all_errors = []

    print(f"Validating skill: {skill_dir.name}")
    print("-" * 50)

    # Run all validations
    checks = [
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta_json),
        ("References", validate_references),
        ("Security", validate_no_secrets),
    ]

    all_passed = True
    for name, validator in checks:
        passed, errors = validator(skill_dir)
        if passed:
            print(f"✓ {name}: PASS")
        else:
            print(f"✗ {name}: FAIL")
            all_errors.extend(errors)
            for err in errors:
                print(f"  - {err}")
            all_passed = False

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed!")
        return 0
    else:
        print(f"✗ {len(all_errors)} validation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
