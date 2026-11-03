#!/usr/bin/env python3
"""
Skill Validation Script for short-video-copywriter
Validates frontmatter, structure, and naming conventions
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter starts at line 1
    if not content.startswith("---"):
        errors.append("Frontmatter must start at line 1 (no markdown title before ---)")
        return False, errors

    # Extract frontmatter
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("Frontmatter closing '---' not found")
        return False, errors

    frontmatter_text = "\n".join(lines[1:frontmatter_end])

    # Check required fields
    if "name:" not in frontmatter_text:
        errors.append("Missing 'name:' field in frontmatter")

    if "description:" not in frontmatter_text:
        errors.append("Missing 'description:' field in frontmatter")

    # Check name format (hyphen-case)
    name_match = re.search(r"name:\s*(.+)", frontmatter_text)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Name '{name}' should be lowercase with hyphens only")
        if name != Path(skill_path).name:
            errors.append(f"Name '{name}' should match folder name '{Path(skill_path).name}'")

    # Check description contains trigger keywords
    desc_match = re.search(r"description:\s*(.+)", frontmatter_text)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append("Description too short (< 20 chars)")
        if "抖音" not in desc and "文案" not in desc:
            errors.append("Description should mention trigger scenarios")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """Validate _meta.json structure"""
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        errors.append("_meta.json not found")
        return False, errors

    import json
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json is invalid JSON: {e}")
        return False, errors

    # Check required fields
    if "id" not in meta:
        errors.append("Missing 'id' field in _meta.json")
    if "version" not in meta:
        errors.append("Missing 'version' field in _meta.json")

    # Validate id is integer or string
    if "id" in meta:
        if not isinstance(meta["id"], (int, str)):
            errors.append("'id' should be integer or string")

    # Validate version format
    if "version" in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
            errors.append("'version' should follow semantic versioning (e.g., 1.0.0)")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """Validate directory structure"""
    errors = []
    skill_name = Path(skill_path).name

    # Check folder name is English only
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        errors.append(f"Folder name '{skill_name}' contains non-ASCII characters")

    # Check for forbidden files
    forbidden = ["node_modules", ".git", "__pycache__", ".env"]
    for root, dirs, files in os.walk(skill_path):
        for f in files:
            if f in forbidden:
                errors.append(f"Forbidden file found: {f}")
        for d in dirs:
            if d in forbidden:
                errors.append(f"Forbidden directory found: {d}")

    return len(errors) == 0, errors


def main():
    skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_name = Path(skill_path).name

    print("=" * 50)
    print(f"Skill Validation: {skill_name}")
    print("=" * 50)

    all_passed = True

    # Run validations
    validations = [
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta_json),
        ("Structure", validate_structure),
    ]

    for name, validator in validations:
        passed, errors = validator(skill_path)
        status = "PASS" if passed else "FAIL"
        print(f"\n[{status}] {name}")

        if not passed:
            all_passed = False
            for error in errors:
                print(f"  - {error}")

    print("\n" + "=" * 50)
    if all_passed:
        print("All validations PASSED")
        sys.exit(0)
    else:
        print("Some validations FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
