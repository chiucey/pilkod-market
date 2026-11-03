#!/usr/bin/env python3
"""
Quick Validation Script for SKILL.md
Validates frontmatter and structure without packaging
"""

import os
import sys
import json
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """Validate skill structure"""
    skill_path = Path(skill_path)
    errors = []
    warnings = []

    print(f"Validating skill: {skill_path.name}")
    print("-" * 50)

    # Check SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
    else:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check frontmatter position
        if not content.startswith('---'):
            errors.append("SKILL.md must start with frontmatter (---)")

        # Parse frontmatter
        lines = content.split('---')
        if len(lines) >= 2:
            frontmatter = lines[1]
            for field in ['name:', 'description:']:
                if field not in frontmatter:
                    errors.append(f"Frontmatter missing '{field}'")

            # Extract name for folder match check
            for line in frontmatter.split('\n'):
                if line.strip().startswith('name:'):
                    frontmatter_name = line.split(':', 1)[1].strip()
                    if frontmatter_name != skill_path.name:
                        warnings.append(
                            f"Frontmatter name '{frontmatter_name}' != folder name '{skill_path.name}'"
                        )
        else:
            errors.append("Frontmatter not properly closed")

    # Check _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        warnings.append("_meta.json not found (optional but recommended)")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            required_fields = ['id', 'version']
            for field in required_fields:
                if field not in meta:
                    errors.append(f"_meta.json missing '{field}'")

            # Validate ID is numeric
            if 'id' in meta:
                try:
                    int(meta['id'])
                except ValueError:
                    errors.append("_meta.json 'id' must be an integer")

        except json.JSONDecodeError as e:
            errors.append(f"_meta.json parse error: {e}")

    # Report results
    print("\nResults:")
    if errors:
        print("  ERRORS:")
        for err in errors:
            print(f"    ✗ {err}")

    if warnings:
        print("  WARNINGS:")
        for warn in warnings:
            print(f"    ! {warn}")

    if not errors and not warnings:
        print("  ✓ All checks passed!")

    print("-" * 50)

    return len(errors) == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_dir = "/workspace/temp-skills/creative-writing-assistant"
    else:
        skill_dir = sys.argv[1]

    success = validate_skill(skill_dir)
    sys.exit(0 if success else 1)
