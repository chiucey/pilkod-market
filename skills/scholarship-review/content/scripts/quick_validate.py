#!/usr/bin/env python3
"""
Quick validation script for scholarship-review skill.
Validates SKILL.md frontmatter, _meta.json, and structure.
"""

import json
import os
import re
import sys


def validate_frontmatter(skill_path):
    """Validate SKILL.md frontmatter format."""
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        return False, "SKILL.md not found"

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Check: frontmatter must start at line 1
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return False, "Frontmatter must start with '---' at line 1"

    # Find closing ---
    try:
        closing_idx = lines.index("---", 1)
    except ValueError:
        return False, "Frontmatter missing closing '---'"

    frontmatter_text = "\n".join(lines[1:closing_idx])

    # Check required fields
    required_fields = ["name", "description"]
    for field in required_fields:
        pattern = rf"^{field}:\s*.+$"
        if not re.search(pattern, frontmatter_text, re.MULTILINE):
            return False, f"Missing required frontmatter field: {field}"

    # Validate name format (hyphen-case, no spaces)
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            return False, f"name must be hyphen-case: '{name_value}'"

    # Check for invalid patterns (no # before ---)
    if re.search(r'^#\s+', content):
        return False, "Markdown headings (#) must not appear before frontmatter"

    return True, "Frontmatter validation passed"


def validate_meta_json(skill_path):
    """Validate _meta.json structure."""
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return False, "_meta.json not found"

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in _meta.json: {e}"

    # Check required fields
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field in _meta.json: {field}"

    # Validate version format (semver)
    version = meta.get("version", "")
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"version must be semver format: '{version}'"

    return True, "_meta.json validation passed"


def validate_paths(skill_path):
    """Validate all paths contain only ASCII/English characters."""
    issues = []

    for root, dirs, files in os.walk(skill_path):
        # Check directory names
        for d in dirs:
            if not d.isascii():
                issues.append(f"Non-ASCII directory name: {d}")

        # Check file names
        for f in files:
            if not f.isascii():
                issues.append(f"Non-ASCII file name: {f}")

    if issues:
        return False, f"Path validation failed: {'; '.join(issues)}"

    return True, "Path validation passed (all ASCII)"


def main():
    skill_path = os.path.dirname(os.path.abspath(__file__))
    # If running from skill root, adjust path
    if os.path.basename(skill_path) == "scripts":
        skill_path = os.path.dirname(skill_path)

    results = []

    # Validate frontmatter
    valid, msg = validate_frontmatter(skill_path)
    results.append(("Frontmatter", valid, msg))
    print(f"[{'OK' if valid else 'FAIL'}] {msg}")

    # Validate _meta.json
    valid, msg = validate_meta_json(skill_path)
    results.append(("_meta.json", valid, msg))
    print(f"[{'OK' if valid else 'FAIL'}] {msg}")

    # Validate paths
    valid, msg = validate_paths(skill_path)
    results.append(("Paths", valid, msg))
    print(f"[{'OK' if valid else 'FAIL'}] {msg}")

    # Summary
    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 40)
    if all_passed:
        print("All validations passed!")
        sys.exit(0)
    else:
        print("Some validations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()