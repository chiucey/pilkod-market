#!/usr/bin/env python3
"""
Quick validation script for VideoGenerator_ByDreamina skill.
Validates frontmatter, structure, and naming conventions.
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """Validate the skill structure and content."""
    errors = []
    warnings = []

    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors, warnings

    # Read SKILL.md
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid or missing YAML frontmatter")
    else:
        frontmatter = frontmatter_match.group(1)

        # Check required fields
        if not re.search(r'^name:', frontmatter, re.MULTILINE):
            errors.append("Frontmatter missing 'name' field")

        if not re.search(r'^description:', frontmatter, re.MULTILINE):
            errors.append("Frontmatter missing 'description' field")

        # Validate name format (hyphen-case)
        name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"Name '{name}' must be lowercase hyphen-separated")
            if name != skill_path.name:
                warnings.append(f"Name '{name}' does not match folder name '{skill_path.name}'")

    # Check _meta.json exists
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        import json
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'skill_id' not in meta:
            errors.append("_meta.json missing 'skill_id' field")

        if 'version' not in meta:
            errors.append("_meta.json missing 'version' field")

    # Check for non-ASCII in paths (except content)
    if not re.match(r'^[a-zA-Z0-9/_-]+$', str(skill_path)):
        errors.append(f"Skill path contains non-ASCII characters: {skill_path}")

    return len(errors) == 0, errors, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    valid, errors, warnings = validate_skill(skill_path)

    print(f"\n{'='*50}")
    print(f"Skill Validation: {skill_path}")
    print(f"{'='*50}\n")

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  ⚠️  {w}")
        print()

    if errors:
        print("Errors:")
        for e in errors:
            print(f"  ❌ {e}")
        print()
        print("❌ Validation FAILED")
        sys.exit(1)

    print("✅ Validation PASSED")
    sys.exit(0)

if __name__ == "__main__":
    main()
