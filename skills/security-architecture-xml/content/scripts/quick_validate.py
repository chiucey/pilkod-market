#!/usr/bin/env python3
"""
Quick validation script for skill structure and frontmatter.
Validates:
1. SKILL.md frontmatter correctness
2. _meta.json presence and validity
3. Folder name matches frontmatter name
4. Required files exist
"""

import os
import sys
import json
import re
from pathlib import Path


def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """Validate skill structure and return (success, errors)."""
    errors = []
    skill_path = Path(skill_path)

    # 1. Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    # 2. Read and parse frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter starts at line 1
    if not content.startswith('---'):
        errors.append("SKILL.md must start with --- (frontmatter delimiter)")

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Frontmatter not properly formatted (missing opening/closing ---)")
        return False, errors

    frontmatter_text = frontmatter_match.group(1)

    # Parse frontmatter keys
    frontmatter = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Check required frontmatter fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required frontmatter field: {field}")

    # Check name matches folder
    if 'name' in frontmatter:
        folder_name = skill_path.name
        if frontmatter['name'] != folder_name:
            errors.append(f"Name mismatch: frontmatter='{frontmatter['name']}' folder='{folder_name}'")

    # Check name format (hyphen-case)
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not re.match(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$', name):
            errors.append(f"Name '{name}' should use hyphen-case format (e.g., 'my-skill')")

    # 3. Check _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # 4. Check description contains trigger phrase
    if 'description' in frontmatter:
        desc = frontmatter['description']
        if len(desc) < 20:
            errors.append("Description is too short (should be descriptive)")
        if 'use when' not in desc.lower() and '触发' not in desc:
            errors.append("Description should contain trigger phrase like 'use when' or '触发'")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <path_to_skill>")
        sys.exit(1)

    skill_path = sys.argv[1]
    success, errors = validate_skill(skill_path)

    print(f"\n{'='*50}")
    print(f"Validating: {skill_path}")
    print(f"{'='*50}")

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
