#!/usr/bin/env python3
"""
Quick validation script for official-account-article-assistant skill.
Validates frontmatter, structure, and required files.
"""

import os
import sys
import re

def validate_skill(skill_path: str) -> bool:
    """Validate skill structure and frontmatter."""
    errors = []
    warnings = []

    # Check skill directory exists
    if not os.path.isdir(skill_path):
        errors.append(f"Skill directory not found: {skill_path}")
        return False

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(skill_md):
        errors.append("SKILL.md not found")
        return False

    # Read SKILL.md content
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter exists and is at the beginning
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False

    # Extract frontmatter
    frontmatter_end = content.find('---', 3)
    if frontmatter_end == -1:
        errors.append("Frontmatter closing (---) not found")
        return False

    frontmatter = content[3:frontmatter_end].strip()

    # Check required frontmatter fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            errors.append(f"Missing required frontmatter field: {field}")

    # Check _meta.json exists
    meta_path = os.path.join(skill_path, "_meta.json")
    if not os.path.isfile(meta_path):
        errors.append("_meta.json not found")
        return False

    # Validate _meta.json content
    import json
    with open(meta_path, 'r', encoding='utf-8') as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")
            return False

    # Check required _meta.json fields
    required_meta_fields = ['id', 'version']
    for field in required_meta_fields:
        if field not in meta:
            errors.append(f"Missing required _meta.json field: {field}")

    # Check frontmatter name matches folder name (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        folder_name = os.path.basename(skill_path)
        if name != folder_name:
            warnings.append(f"Frontmatter name '{name}' does not match folder name '{folder_name}'")

    # Report results
    if errors:
        print("❌ VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")
        return False

    if warnings:
        print("⚠️ VALIDATION PASSED WITH WARNINGS")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("✅ VALIDATION PASSED")

    return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/official-account-article-assistant"
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
