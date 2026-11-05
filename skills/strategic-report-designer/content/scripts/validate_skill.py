#!/usr/bin/env python3
"""
Validation script for strategic-report-designer skill.
Checks frontmatter, structure, and content requirements.
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """Validate frontmatter format and required fields."""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter starts at line 0
    if not content.startswith("---"):
        errors.append("Frontmatter must start at line 0 (no markdown headers before)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Frontmatter not properly closed with ---")
        return False, errors

    frontmatter_text = frontmatter_match.group(1)

    # Check required fields
    if "name:" not in frontmatter_text:
        errors.append("Missing required field: name")

    if "description:" not in frontmatter_text:
        errors.append("Missing required field: description")

    # Check name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(f"Name '{name}' should use hyphen-case format")
        if len(name) > 64:
            errors.append(f"Name '{name}' exceeds 64 character limit")

    # Check description contains trigger phrases
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append("Description too short (should be descriptive)")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """Validate _meta.json structure."""
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json not found"]

    import json
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in _meta.json: {e}"]

    # Check required fields
    if "id" not in meta:
        errors.append("Missing required field: id in _meta.json")
    elif not isinstance(meta["id"], int):
        errors.append("Field 'id' must be an integer")

    if "version" not in meta:
        errors.append("Missing required field: version in _meta.json")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
        errors.append("Version should follow semantic versioning (e.g., 1.0.0)")

    return len(errors) == 0, errors


def validate_color_system(skill_path: str) -> tuple[bool, list[str]]:
    """Validate five-color system is properly defined."""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    required_colors = [
        ("深海蓝", "#0B528D"),
        ("天空蓝", "#5A97CA"),
        ("薰衣草蓝", "#7CA5E8"),
        ("雾灰白", "#CFD1DE"),
        ("珊瑚橙", "#F18765")
    ]

    for color_name, color_hex in required_colors:
        if color_hex not in content:
            errors.append(f"Missing required color: {color_name} ({color_hex})")

    return len(errors) == 0, errors


def validate_font_hierarchy(skill_path: str) -> tuple[bool, list[str]]:
    """Validate font hierarchy with 74% ratio."""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # Check for 74% ratio requirement
    if "0.74" not in content and "74%" not in content:
        errors.append("Missing 74% font ratio specification for H2")

    # Check for coral orange (珊瑚橙) in subtitle requirement
    if "珊瑚橙" not in content or "#F18765" not in content:
        errors.append("Missing coral orange subtitle color specification")

    return len(errors) == 0, errors


def validate_image_formats(skill_path: str) -> tuple[bool, list[str]]:
    """Validate 13 image formats are defined."""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # Count defined image formats (A through M) - check in table context
    # Pattern: "| A |" in a table (image formats section)
    format_letters = set()
    for letter in "ABCDEFGHIJKLM":
        # Check for "形式A" or "| A |" pattern (single letter in table)
        if f"形式{letter}" in content or f"形式 {letter}" in content:
            format_letters.add(letter)
        # Also check for table format "| A |"
        if re.search(rf'\|\s*{letter}\s*\|', content):
            format_letters.add(letter)

    format_count = len(format_letters)

    if format_count < 13:
        errors.append(f"Expected 13 image formats (A-M), found {format_count}: {sorted(format_letters)}")

    return len(errors) == 0, errors


def validate_chapter_control(skill_path: str) -> tuple[bool, list[str]]:
    """Validate chapter control rules."""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # Check for chapter control rules
    if "CH.01" not in content and "CH.02" not in content:
        errors.append("Missing chapter numbering specification (CH.01, CH.02, etc.)")

    if "3章" not in content and "三章" not in content:
        errors.append("Missing chapter count control (<30页则≤3章)")

    return len(errors) == 0, errors


def validate_no_forbidden_elements(skill_path: str) -> tuple[bool, list[str]]:
    """Check for forbidden elements."""
    warnings = []
    skill_md = Path(skill_path) / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # Check for prohibited color block backgrounds
    if "色块衬底" not in content:
        warnings.append("Warning: No mention of 'no color block' rule")

    if "禁止" not in content and "红线" not in content:
        warnings.append("Warning: No forbidden behaviors documented")

    return len(warnings) == 0, warnings


def run_validation(skill_path: str) -> bool:
    """Run all validations and report results."""
    print(f"Validating skill at: {skill_path}")
    print("=" * 60)

    all_passed = True

    # Run all validations
    validations = [
        ("Frontmatter & Structure", validate_frontmatter),
        ("_meta.json", validate_meta_json),
        ("Five-Color System", validate_color_system),
        ("Font Hierarchy (74%)", validate_font_hierarchy),
        ("Image Formats (13)", validate_image_formats),
        ("Chapter Control", validate_chapter_control),
        ("Forbidden Elements", validate_no_forbidden_elements),
    ]

    for name, validator in validations:
        passed, errors = validator(skill_path)
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status}: {name}")

        if not passed:
            all_passed = False
            for error in errors:
                print(f"  - {error}")

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All validations passed!")
        return True
    else:
        print("✗ Some validations failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = run_validation(skill_path)
    sys.exit(0 if success else 1)
