#!/usr/bin/env python3
"""
Research Stack Skill Validator
Validates skill structure, frontmatter, and naming conventions.

Usage:
    python quick_validate.py <skill_path>
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple


def validate_frontmatter(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate YAML frontmatter in a SKILL.md file."""
    errors = []

    with open(file_path) as f:
        content = f.read()

    if not content.startswith("---"):
        errors.append(f"{file_path}: Must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    lines = content.split("\n")
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append((i, line))

    if not frontmatter_lines:
        errors.append(f"{file_path}: Empty or missing frontmatter")
        return False, errors

    # Check required fields
    frontmatter_text = "\n".join(line for _, line in frontmatter_lines)
    has_name = re.search(r"^name:", frontmatter_text, re.MULTILINE)
    has_description = re.search(r"^description:", frontmatter_text, re.MULTILINE)

    if not has_name:
        errors.append(f"{file_path}: Missing 'name' field in frontmatter")
    if not has_description:
        errors.append(f"{file_path}: Missing 'description' field in frontmatter")

    # Validate name format (hyphen-case)
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9][a-z0-9-]*$", name):
            errors.append(f"{file_path}: Name '{name}' should use hyphen-case (e.g., 'my-skill')")

    # Check for markdown heading BEFORE frontmatter (not after)
    # Only check lines before the first "---" that starts frontmatter
    frontmatter_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            frontmatter_start = i
            break

    for i, line in enumerate(lines[:frontmatter_start]):
        if line.strip().startswith("#"):
            errors.append(f"{file_path}: Markdown heading (#) found before frontmatter")
            break

    return len(errors) == 0, errors


def validate_meta_json(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate _meta.json file."""
    errors = []

    if not file_path.exists():
        errors.append(f"{file_path}: _meta.json not found")
        return False, errors

    try:
        with open(file_path) as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"{file_path}: Invalid JSON: {e}")
        return False, errors

    if "id" not in meta:
        errors.append(f"{file_path}: Missing 'id' field")
    elif not isinstance(meta["id"], int) or meta["id"] <= 0:
        errors.append(f"{file_path}: 'id' must be a positive integer")

    if "version" not in meta:
        errors.append(f"{file_path}: Missing 'version' field")
    elif not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
        errors.append(f"{file_path}: 'version' should follow semantic versioning (e.g., '1.0.0')")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: Path) -> Tuple[bool, List[str]]:
    """Validate skill directory structure."""
    errors = []

    # Root level
    root_skill = skill_path / "SKILL.md"
    if not root_skill.exists():
        errors.append(f"{skill_path}: Missing SKILL.md at root")

    # Roles validation
    roles_dir = skill_path / "roles"
    if roles_dir.exists():
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith("."):
                role_skill = role_dir / "SKILL.md"
                if not role_skill.exists():
                    errors.append(f"{role_dir}: Missing SKILL.md")
                meta = role_dir / "_meta.json"
                if not meta.exists():
                    errors.append(f"{role_dir}: Missing _meta.json")

    return len(errors) == 0, errors


def validate_all(skill_path: Path) -> Tuple[bool, List[str]]:
    """Run all validations."""
    all_errors = []

    # Structure validation
    ok, errors = validate_directory_structure(skill_path)
    all_errors.extend(errors)

    # Root frontmatter
    root_skill = skill_path / "SKILL.md"
    if root_skill.exists():
        ok, errors = validate_frontmatter(root_skill)
        all_errors.extend(errors)

    # Root meta
    root_meta = skill_path / "_meta.json"
    if root_meta.exists():
        ok, errors = validate_meta_json(root_meta)
        all_errors.extend(errors)

    # ORCHESTRATOR.md if exists
    orchestrator = skill_path / "ORCHESTRATOR.md"
    if orchestrator.exists():
        ok, errors = validate_frontmatter(orchestrator)
        all_errors.extend(errors)

    # Role validations
    roles_dir = skill_path / "roles"
    if roles_dir.exists():
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith("."):
                role_skill = role_dir / "SKILL.md"
                if role_skill.exists():
                    ok, errors = validate_frontmatter(role_skill)
                    all_errors.extend(errors)

                role_meta = role_dir / "_meta.json"
                if role_meta.exists():
                    ok, errors = validate_meta_json(role_meta)
                    all_errors.extend(errors)

    return len(all_errors) == 0, all_errors


def main():
    parser = argparse.ArgumentParser(description="Validate Research Stack skill")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not skill_path.exists():
        print(f"Error: Path not found: {skill_path}")
        return 1

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    valid, errors = validate_all(skill_path)

    if errors:
        print("Validation FAILED:")
        for error in errors:
            print(f"  [X] {error}")
        return 1
    else:
        print("Validation PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
