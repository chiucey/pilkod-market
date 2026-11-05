#!/usr/bin/env python3
"""
Quick validation script for drug-regulatory-intelligence skill
"""
import os
import json
from pathlib import Path

def validate_skill():
    """Validate skill structure and frontmatter"""
    skill_dir = Path(__file__).parent.parent
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return errors, warnings

    # Check frontmatter
    content = skill_md.read_text(encoding='utf-8')
    if not content.startswith('---'):
        errors.append("SKILL.md must start with frontmatter (---)")

    # Extract frontmatter
    if content.startswith('---'):
        frontmatter_end = content.find('---', 3)
        if frontmatter_end > 0:
            frontmatter_text = content[3:frontmatter_end].strip()
            try:
                frontmatter = {}
                for line in frontmatter_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()

                # Required fields
                if 'name' not in frontmatter:
                    errors.append("Frontmatter missing 'name' field")
                if 'description' not in frontmatter:
                    errors.append("Frontmatter missing 'description' field")
            except Exception as e:
                errors.append(f"Frontmatter parsing error: {e}")

    # Check _meta.json
    meta_json = skill_dir / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json parsing error: {e}")

    # Check directories
    required_dirs = ['references', 'scripts', 'assets']
    for d in required_dirs:
        dir_path = skill_dir / d
        if not dir_path.exists():
            warnings.append(f"Missing directory: {d}")

    return errors, warnings

def main():
    print("Validating drug-regulatory-intelligence skill...")
    errors, warnings = validate_skill()

    if errors:
        print("\n❌ ERRORS:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\n⚠️ WARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("\n✅ Validation passed!")
    elif not errors:
        print("\n✅ Validation passed with warnings")
    else:
        print("\n❌ Validation failed")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
