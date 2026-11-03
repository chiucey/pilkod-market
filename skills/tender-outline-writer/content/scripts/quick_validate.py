#!/usr/bin/env python3
"""
quick_validate.py - Skill validation script for tender-outline-writer

Validates:
1. Frontmatter format and required fields
2. _meta.json structure
3. File naming conventions
4. Directory structure integrity
"""

import json
import os
import re
import sys
from pathlib import Path


class ValidationError:
    def __init__(self, level: str, message: str):
        self.level = level
        self.message = message

    def __str__(self):
        return f"[{self.level.upper()}] {self.message}"


def validate_frontmatter(skill_path: Path) -> list[ValidationError]:
    """Validate SKILL.md frontmatter format and required fields."""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append(ValidationError("error", "SKILL.md not found"))
        return errors

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter starts at line 1
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        errors.append(ValidationError("error", "Frontmatter must start with '---' on line 1"))
        return errors

    # Find end of frontmatter
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        errors.append(ValidationError("error", "Frontmatter missing closing '---'"))
        return errors

    # Parse frontmatter
    try:
        frontmatter_text = "\n".join(lines[1:end_idx])
        frontmatter = {}
        for line in frontmatter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()
    except Exception as e:
        errors.append(ValidationError("error", f"Failed to parse frontmatter: {e}"))
        return errors

    # Check required fields
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in frontmatter:
            errors.append(ValidationError("error", f"Missing required frontmatter field: {field}"))
        elif not frontmatter[field]:
            errors.append(ValidationError("error", f"Frontmatter field '{field}' is empty"))

    # Validate name format (hyphen-case)
    if "name" in frontmatter:
        name = frontmatter["name"]
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            errors.append(ValidationError("warning", f"Skill name '{name}' should use hyphen-case format"))

        # Check name matches directory
        if name != skill_path.name:
            errors.append(ValidationError("error", f"Skill name '{name}' does not match directory name '{skill_path.name}'"))

    # Check description contains trigger phrase
    if "description" in frontmatter and frontmatter["description"]:
        desc = frontmatter["description"]
        if "Use when" not in desc and "use when" not in desc.lower():
            errors.append(ValidationError("warning", "Description should contain trigger phrase 'Use when...'"))

    return errors


def validate_meta(skill_path: Path) -> list[ValidationError]:
    """Validate _meta.json structure."""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        errors.append(ValidationError("error", "_meta.json not found"))
        return errors

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(ValidationError("error", f"Invalid JSON in _meta.json: {e}"))
        return errors

    # Check required fields
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(ValidationError("error", f"Missing required field in _meta.json: {field}"))

    # Validate version format (semantic versioning)
    if "version" in meta:
        version = meta["version"]
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            errors.append(ValidationError("warning", f"Version '{version}' should follow semantic versioning (e.g., 1.0.0)"))

    # Validate id is numeric
    if "id" in meta:
        try:
            int(meta["id"])
        except ValueError:
            errors.append(ValidationError("error", f"Skill ID '{meta['id']}' must be a numeric string"))

    return errors


def validate_structure(skill_path: Path) -> list[ValidationError]:
    """Validate skill directory structure."""
    errors = []

    # Check for unwanted files in root
    unwanted_patterns = [r"\.pyc$", r"__pycache__", r"\.DS_Store"]
    for pattern in unwanted_patterns:
        for f in skill_path.rglob("*"):
            if re.search(pattern, str(f)):
                rel_path = f.relative_to(skill_path)
                if not str(rel_path).startswith("scripts/"):
                    errors.append(ValidationError("warning", f"Unexpected file: {rel_path}"))

    return errors


def validate_security(skill_path: Path) -> list[ValidationError]:
    """Check for potential security issues."""
    errors = []

    # Check for secrets patterns in SKILL.md
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        secret_patterns = [
            (r"api[_-]?key", "API key pattern"),
            (r"password\s*=", "password assignment"),
            (r"secret\s*=", "secret assignment"),
            (r"-----BEGIN.*PRIVATE KEY-----", "private key"),
        ]

        for pattern, name in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(ValidationError("warning", f"Potential secret pattern found: {name}"))

    return errors


def validate_skill(skill_path: str) -> bool:
    """Run all validations and return True if all pass."""
    skill_path = Path(skill_path).resolve()

    print(f"\n{'='*60}")
    print(f"Validating skill: {skill_path.name}")
    print(f"{'='*60}\n")

    all_errors = []

    # Run all validations
    all_errors.extend(validate_frontmatter(skill_path))
    all_errors.extend(validate_meta(skill_path))
    all_errors.extend(validate_structure(skill_path))
    all_errors.extend(validate_security(skill_path))

    # Report results
    if all_errors:
        errors = [e for e in all_errors if e.level == "error"]
        warnings = [e for e in all_errors if e.level == "warning"]

        if errors:
            print(f"\n❌ {len(errors)} ERROR(S) found:\n")
            for e in errors:
                print(f"  {e}")

        if warnings:
            print(f"\n⚠️  {len(warnings)} WARNING(S):\n")
            for w in warnings:
                print(f"  {w}")

        print(f"\n{'='*60}")
        print("VALIDATION FAILED")
        print(f"{'='*60}\n")
        return False

    print("\n✅ All validations passed!")
    print(f"{'='*60}\n")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <path_to_skill>")
        sys.exit(1)

    skill_path = sys.argv[1]
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
