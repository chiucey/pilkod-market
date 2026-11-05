#!/usr/bin/env python3
"""
Quick Validation Script for Investment Research Suite
Validates SKILL.md frontmatter, structure, and naming conventions.
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """Validate a skill directory. Returns (success, errors)."""
    errors = []
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    # Read SKILL.md content
    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter starts at line 0
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Parse frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    name_match = None

    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
    else:
        frontmatter = frontmatter_match.group(1)

        # Check required fields
        if 'name:' not in frontmatter:
            errors.append("Frontmatter missing 'name' field")
        if 'description:' not in frontmatter:
            errors.append("Frontmatter missing 'description' field")

        # Extract name
        name_match = re.search(r'^name:\s*(.+?)\s*$', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            # Check name format (hyphen-case)
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
                errors.append(f"Name '{name}' should be hyphen-case (e.g., my-skill)")

    # Check _meta.json exists
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json missing 'id' field")
            if "version" not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json invalid JSON: {e}")

    # Check directory name matches frontmatter name
    if name_match:
        expected_name = name_match.group(1).strip()
        actual_name = skill_path.name
        if expected_name != actual_name:
            errors.append(f"Folder name '{actual_name}' should match frontmatter name '{expected_name}'")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    print(f"Validating skill at: {skill_path}")

    success, errors = validate_skill(skill_path)

    if success:
        print("✅ Validation PASSED")
        sys.exit(0)
    else:
        print("❌ Validation FAILED:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
