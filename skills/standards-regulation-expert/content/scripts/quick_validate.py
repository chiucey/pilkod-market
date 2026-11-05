#!/usr/bin/env python3
"""
Standards Regulation Expert Skill Validation Script
Validates the skill structure and frontmatter compliance
"""

import os
import sys
import re
from pathlib import Path

def validate_skill(skill_path):
    """Validate skill directory structure and content"""
    errors = []
    warnings = []

    # Check directory exists
    if not os.path.isdir(skill_path):
        errors.append(f"Skill directory not found: {skill_path}")
        return errors, warnings

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(skill_md):
        errors.append("SKILL.md not found")
        return errors, warnings

    # Read SKILL.md
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # Check required fields
        if not re.search(r'^name:', frontmatter, re.MULTILINE):
            errors.append("Frontmatter missing 'name' field")

        if not re.search(r'^description:', frontmatter, re.MULTILINE):
            errors.append("Frontmatter missing 'description' field")
    else:
        errors.append("Could not parse YAML frontmatter")

    # Check _meta.json exists
    meta_json = os.path.join(skill_path, "_meta.json")
    if not os.path.isfile(meta_json):
        errors.append("_meta.json not found")
    else:
        import json
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # Check references directory
    references_dir = os.path.join(skill_path, "references")
    if os.path.isdir(references_dir):
        ref_files = os.listdir(references_dir)
        if not ref_files:
            warnings.append("references directory is empty")

    return errors, warnings

def main():
    skill_path = os.path.dirname(os.path.abspath(__file__))
    skill_path = os.path.dirname(skill_path)  # Go up from scripts to skill root

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    errors, warnings = validate_skill(skill_path)

    if errors:
        print("ERRORS:")
        for err in errors:
            print(f"  [X] {err}")

    if warnings:
        print("WARNINGS:")
        for warn in warnings:
            print(f"  [!] {warn}")

    if not errors and not warnings:
        print("[OK] Validation passed - no errors or warnings")
        return 0
    elif not errors:
        print("[OK] Validation passed with warnings")
        return 0
    else:
        print("[FAIL] Validation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
