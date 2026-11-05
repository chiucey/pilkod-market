#!/usr/bin/env python3
"""Validate Druckenmiller Market Analysis Skill Structure"""

import json
import os
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """Validate skill directory structure and content"""
    skill_dir = Path(skill_path).resolve()
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False

    # Read SKILL.md content
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter format
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Extract frontmatter
    lines = content.split('\n')
    if lines[0] == '---':
        frontmatter_lines = []
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_lines = lines[1:i]
                break

        if not frontmatter_lines:
            errors.append("Frontmatter closing --- not found")
        else:
            # Parse frontmatter
            frontmatter = {}
            for line in frontmatter_lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

            # Check required fields
            if 'name' not in frontmatter:
                errors.append("Frontmatter missing 'name' field")
            if 'description' not in frontmatter:
                errors.append("Frontmatter missing 'description' field")

            # Check name matches folder
            expected_name = skill_dir.name
            if frontmatter.get('name') != expected_name:
                errors.append(f"Frontmatter name '{frontmatter.get('name')}' does not match folder name '{expected_name}'")

    # Check _meta.json exists
    meta_json = skill_dir / "_meta.json"
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

    # Check description length
    if 'description' in frontmatter and len(frontmatter['description']) < 50:
        warnings.append("Description is very short, may not provide adequate trigger guidance")

    # Check for markdown title before frontmatter
    content_without_fm = content[content.find('---') + content.find('---', content.find('---') + 1) + 3:]
    if content_without_fm.strip().startswith('#'):
        warnings.append("Markdown title found after frontmatter - acceptable but unconventional")

    # Report results
    print(f"\n=== Skill Validation Results ===")
    print(f"Skill: {skill_dir.name}")
    print(f"Path: {skill_dir}")

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")

    if not errors:
        print(f"\n✅ Validation PASSED")
        return True
    else:
        print(f"\n❌ Validation FAILED")
        return False

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
