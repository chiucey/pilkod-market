#!/usr/bin/env python3
"""
Quick validation script for skill structure.
Validates SKILL.md frontmatter, _meta.json, and directory structure.
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
    lines = content.split("\n")

    # Check frontmatter starts at line 1
    if not lines[0].strip() == "---":
        errors.append(f"Frontmatter must start with '---', found: '{lines[0]}'")
        return False, errors

    # Find end of frontmatter
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        errors.append("Frontmatter closing '---' not found")
        return False, errors

    # Parse frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter = {}
    current_key = None

    for line in frontmatter_lines:
        if line.startswith("  ") or line.startswith("\t"):
            # Continuation line
            if current_key:
                frontmatter[current_key] += "\n" + line.strip()
        elif ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            frontmatter[current_key] = value.strip()

    # Validate required fields
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required frontmatter field: {field}")

    # Validate name format (hyphen-case)
    if "name" in frontmatter:
        name = frontmatter["name"]
        if not re.match(r'^[a-z][a-z0-9-]*$', name):
            errors.append(f"Name '{name}' should be hyphen-case (e.g., 'career-advisor')")

    # Validate description contains trigger phrases
    if "description" in frontmatter:
        desc = frontmatter["description"].lower()
        trigger_keywords = ["use when", "触发", "when user"]
        if not any(keyword in desc for keyword in trigger_keywords):
            errors.append("Description should contain trigger phrases (e.g., 'Use when...')")

    # Check for markdown title before frontmatter
    if any(line.startswith("#") for line in lines[:end_idx]):
        errors.append("Markdown title (#) should not appear before frontmatter")

    return len(errors) == 0, errors


def validate_meta(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json format and content."""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in _meta.json: {e}"]

    # Validate required fields
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required field in _meta.json: {field}")

    # Validate version format (semantic versioning)
    if "version" in meta:
        version = meta["version"]
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"Version '{version}' should be semantic (e.g., '1.0.0')")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate directory structure."""
    errors = []

    # Check required files exist
    required_files = ["SKILL.md"]
    for file in required_files:
        if not (skill_path / file).exists():
            errors.append(f"Missing required file: {file}")

    # Validate optional directories are safe
    allowed_dirs = ["references", "scripts", "assets"]
    for item in skill_path.iterdir():
        if item.is_dir():
            if item.name not in allowed_dirs:
                errors.append(f"Unexpected directory: {item.name} (allowed: {allowed_dirs})")
            # Check for symlink escape
            if item.is_symlink():
                errors.append(f"Symlinks are not allowed: {item.name}")

    # Check for unwanted files
    unwanted_patterns = [".env", ".pem", ".key", "secrets", "credentials"]
    for item in skill_path.rglob("*"):
        if item.is_file():
            for pattern in unwanted_patterns:
                if pattern in item.name.lower():
                    errors.append(f"Sensitive file detected: {item}")

    return len(errors) == 0, errors


def validate_references(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate references directory structure."""
    errors = []
    refs_dir = skill_path / "references"

    if not refs_dir.exists():
        # References is optional
        return True, []

    # Check all reference files are markdown
    for item in refs_dir.iterdir():
        if item.is_file() and not item.suffix == ".md":
            errors.append(f"Reference file should be .md: {item.name}")

    return len(errors) == 0, errors


def main():
    """Run all validations."""
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    all_errors = []

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    # Run all validations
    validations = [
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta),
        ("Structure", validate_structure),
        ("References", validate_references),
    ]

    all_passed = True
    for name, validator in validations:
        passed, errors = validator(skill_path)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        if not passed:
            all_passed = False
            all_errors.extend([f"  - {e}" for e in errors])
            for error in errors:
                print(f"  - {error}")

    print("-" * 50)
    if all_passed:
        print("All validations PASSED")
        sys.exit(0)
    else:
        print(f"Validation FAILED with {len(all_errors)} error(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
