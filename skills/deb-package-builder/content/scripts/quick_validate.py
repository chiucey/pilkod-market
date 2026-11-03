#!/usr/bin/env python3
"""
Quick Skill Validator

Validates skill structure and frontmatter without full testing.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path


def validate_skill(skill_dir: str) -> bool:
    """
    Validate skill structure and frontmatter.

    Returns:
        True if valid, False otherwise
    """
    skill_path = Path(skill_dir)
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False

    # Read and validate frontmatter
    content = skill_md.read_text()

    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False

    # Extract frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Invalid frontmatter format")
        return False

    try:
        import yaml
        frontmatter = yaml.safe_load(parts[1])
    except ImportError:
        # Simple key-value parsing fallback
        frontmatter = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

    # Check required fields
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")

    # Check _meta.json
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        warnings.append("_meta.json not found")
    else:
        try:
            meta = json.loads(meta_path.read_text())
            if "id" not in meta:
                errors.append("_meta.json missing 'id' field")
            if "version" not in meta:
                warnings.append("_meta.json missing 'version' field")
        except json.JSONDecodeError:
            errors.append("_meta.json is not valid JSON")

    # Report results
    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  - {error}")
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

    if not errors and not warnings:
        print("Validation passed!")

    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description="Quick validate a skill")
    parser.add_argument("skill_dir", nargs="?", default=".", help="Path to skill directory")
    args = parser.parse_args()

    is_valid = validate_skill(args.skill_dir)
    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
