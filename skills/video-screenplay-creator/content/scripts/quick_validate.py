#!/usr/bin/env python3
"""Quick validation script for video-screenplay-creator skill."""

import os
import re
import json
import sys

def validate_skill(skill_path: str) -> bool:
    """Validate skill structure and content."""
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md not found")
        return False, errors, warnings

    # Check _meta.json exists
    meta_json = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_json):
        errors.append("_meta.json not found")
        return False, errors, warnings

    # Validate _meta.json
    with open(meta_json, 'r') as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json invalid JSON: {e}")
            return False, errors, warnings

        if 'id' not in meta:
            errors.append("_meta.json missing 'id' field")
        if 'version' not in meta:
            errors.append("_meta.json missing 'version' field")

    # Validate SKILL.md frontmatter
    with open(skill_md, 'r') as f:
        content = f.read()

    # Check frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Cannot parse frontmatter from SKILL.md")
    else:
        frontmatter = frontmatter_match.group(1)

        # Check required fields
        if 'name:' not in frontmatter:
            errors.append("Frontmatter missing 'name' field")
        if 'description:' not in frontmatter:
            errors.append("Frontmatter missing 'description' field")

        # Check name format (hyphen-case)
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"Name '{name}' should be lowercase with hyphens only")

    # Check content after frontmatter
    content_after_fm = content[frontmatter_match.end():].strip()
    if not content_after_fm:
        warnings.append("SKILL.md has no content after frontmatter")

    # Check for markdown title at start (wrong)
    lines = content.split('\n')
    for i, line in enumerate(lines[:5]):
        if line.startswith('# ') and i > 2:
            warnings.append(f"Possible markdown title at line {i+1}: '{line}' (should not appear before frontmatter ends)")

    return len(errors) == 0, errors, warnings

def main():
    skill_path = os.path.dirname(os.path.abspath(__file__))
    skill_path = os.path.dirname(skill_path)  # Go up from scripts/

    print(f"Validating skill at: {skill_path}")

    success, errors, warnings = validate_skill(skill_path)

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ⚠ {w}")

    if success:
        print("\n✅ Validation passed!")
        return 0
    else:
        print("\n❌ Validation failed:")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
