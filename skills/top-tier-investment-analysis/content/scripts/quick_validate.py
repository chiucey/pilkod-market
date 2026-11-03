#!/usr/bin/env python3
"""
Quick Validation Script for Skill Package
Validates SKILL.md frontmatter and _meta.json structure
"""

import json
import os
import re
import sys
from pathlib import Path


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_frontmatter(skill_path: Path) -> dict:
    """Validate SKILL.md frontmatter format and required fields"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        raise ValidationError(f"SKILL.md not found at {skill_md}")

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if file starts with frontmatter delimiter
    if not content.strip().startswith("---"):
        raise ValidationError("SKILL.md must start with frontmatter (---)")

    # Extract frontmatter - split only at first two ---
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        raise ValidationError("Invalid frontmatter format: missing closing ---")

    frontmatter_text = fm_match.group(1)

    # Parse frontmatter
    fm = {}
    for line in frontmatter_text.strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip()

    # Validate required fields
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in fm:
            raise ValidationError(f"Missing required frontmatter field: {field}")

    # Validate name format (hyphen-case, no spaces)
    name = fm["name"]
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', name):
        raise ValidationError(f"Invalid name format '{name}': must be hyphen-case (e.g., 'my-skill')")

    # Validate name length
    if len(name) > 64:
        raise ValidationError(f"Name too long: {len(name)} chars (max 64)")

    # Validate description is not empty
    desc = fm["description"]
    if len(desc) < 10:
        raise ValidationError("Description too short (min 10 chars)")

    print(f"  [OK] Frontmatter valid: name='{name}'")
    return fm


def validate_meta(skill_path: Path) -> dict:
    """Validate _meta.json structure and fields"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        raise ValidationError(f"_meta.json not found at {meta_file}")

    with open(meta_file, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        meta = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in _meta.json: {e}")

    # Validate required fields
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            raise ValidationError(f"Missing required _meta.json field: {field}")

    # Validate id is a positive integer
    skill_id = meta["id"]
    if not isinstance(skill_id, int) or skill_id <= 0:
        raise ValidationError(f"Invalid skill ID: {skill_id} (must be positive integer)")

    # Validate version format (semantic versioning)
    version = meta["version"]
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        raise ValidationError(f"Invalid version format '{version}': must be semantic (e.g., '1.0.0')")

    print(f"  [OK] _meta.json valid: id={skill_id}, version={version}")
    return meta


def validate_structure(skill_path: Path) -> None:
    """Validate directory structure and naming"""
    # Check for unwanted patterns
    forbidden_patterns = [
        (r'[\u4e00-\u9fff]', "non-ASCII characters"),
        (r'\s', "spaces in paths"),
    ]

    # Check folder name
    folder_name = skill_path.name
    if re.search(r'[\u4e00-\u9fff]', folder_name):
        raise ValidationError(f"Folder name contains non-English characters: {folder_name}")
    if " " in folder_name:
        raise ValidationError(f"Folder name contains spaces: {folder_name}")

    print(f"  [OK] Folder structure valid: {folder_name}")


def validate_no_secrets(skill_path: Path) -> None:
    """Check for potential secrets or sensitive data"""
    sensitive_patterns = [
        r'api[_-]?key',
        r'secret',
        r'password',
        r'token',
        r'credential',
    ]

    for md_file in skill_path.rglob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read().lower()

        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Check if it's just a template reference, not actual secrets
                if "template" not in content and "example" not in content:
                    print(f"  [WARN] Potential secret pattern '{pattern}' found in {md_file.name}")


def validate_skill(skill_path: str) -> bool:
    """Main validation function"""
    skill_path = Path(skill_path)

    print(f"\nValidating skill at: {skill_path}")
    print("-" * 50)

    errors = []

    try:
        # Validate frontmatter
        fm = validate_frontmatter(skill_path)

        # Validate meta
        meta = validate_meta(skill_path)

        # Validate structure
        validate_structure(skill_path)

        # Check for secrets
        validate_no_secrets(skill_path)

        print("-" * 50)
        print("✅ All validations passed!")
        return True

    except ValidationError as e:
        print(f"\n❌ Validation failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        print("Example: python quick_validate.py ../my-skill")
        sys.exit(1)

    skill_path = sys.argv[1]
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
