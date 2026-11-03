#!/usr/bin/env python3
"""
Quick validation script for skill structure and frontmatter.
Validates SKILL.md frontmatter, _meta.json, and directory structure.
"""
import os
import re
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format and required fields."""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter starts at line 1
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        errors.append("Frontmatter must start with '---' at line 1")

    # Find frontmatter boundaries
    try:
        end_idx = lines.index("---", 1)
    except ValueError:
        errors.append("Frontmatter closing '---' not found")
        return False, errors

    frontmatter_text = "\n".join(lines[1:end_idx])

    # Check for title before frontmatter
    for line in lines[:5]:
        if line.strip().startswith("#"):
            errors.append("Markdown title (#) found before frontmatter - must remove")
            break

    # Parse frontmatter
    frontmatter = {}
    for line in lines[1:end_idx]:
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    # Required fields
    required = ["name", "description"]
    for field in required:
        if field not in frontmatter:
            errors.append(f"Missing required frontmatter field: {field}")

    # Name validation
    if "name" in frontmatter:
        name = frontmatter["name"]
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Name must be lowercase with hyphens only: '{name}'")
        if len(name) > 64:
            errors.append(f"Name must be <= 64 characters: {len(name)}")

    # Description validation
    if "description" in frontmatter:
        desc = frontmatter["description"]
        if not desc or len(desc) < 10:
            errors.append("Description must be meaningful (>10 chars)")

    return len(errors) == 0, errors


def validate_meta(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json structure."""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    # Required fields
    required = ["id", "version"]
    for field in required:
        if field not in meta:
            errors.append(f"Missing required _meta.json field: {field}")

    # Version format check (semver)
    if "version" in meta:
        version = meta["version"]
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"Version must be semantic (x.y.z): {version}")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate directory structure and path names."""
    errors = []

    # Check all files have English-only paths
    for root, dirs, files in os.walk(skill_path):
        for name in files + dirs:
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, skill_path)
            if not all(ord(c) < 128 for c in rel_path):
                errors.append(f"Non-ASCII path detected: {rel_path}")

    # Check for dangerous patterns
    forbidden_patterns = ["__pycache__", ".pyc", ".env", "secrets", "credentials"]
    for root, dirs, files in os.walk(skill_path):
        for name in files + dirs:
            for pattern in forbidden_patterns:
                if pattern in name:
                    errors.append(f"Forbidden pattern in path: {name}")

    return len(errors) == 0, errors


def main():
    # Get skill path from argument or use default
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    print(f"Validating skill at: {skill_path}")
    print("=" * 50)

    all_passed = True

    # Run validations
    checks = [
        ("Frontmatter & Content", validate_frontmatter),
        ("_meta.json", validate_meta),
        ("Directory Structure", validate_structure),
    ]

    for name, validator in checks:
        passed, errors = validator(skill_path)
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status}: {name}")

        if errors:
            all_passed = False
            for error in errors:
                print(f"  - {error}")

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All validations passed!")
        sys.exit(0)
    else:
        print("✗ Validation failed - please fix errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
