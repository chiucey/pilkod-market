#!/usr/bin/env python3
"""
Quick validation script for skill structure
Validates frontmatter, file structure, and naming conventions
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """Validate skill structure and frontmatter"""
    skill_dir = Path(skill_path)
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"SKILL.md not found at {skill_path}")
        return False

    # Read SKILL.md content
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
    else:
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            errors.append("Frontmatter closing (---) not found")
        else:
            frontmatter = content[3:frontmatter_end].strip()

            # Check required fields
            if not re.search(r'^name:', frontmatter, re.MULTILINE):
                errors.append("Frontmatter missing 'name' field")
            if not re.search(r'^description:', frontmatter, re.MULTILINE):
                errors.append("Frontmatter missing 'description' field")

            # Validate name format
            name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                if not re.match(r'^[a-z0-9-]+$', name):
                    errors.append(f"Name must be hyphen-case: '{name}'")
                if len(name) > 64:
                    errors.append(f"Name must be <= 64 characters: '{name}'")

    # Check _meta.json exists
    meta_json = skill_dir / "_meta.json"
    if not meta_json.exists():
        warnings.append("_meta.json not found")
    else:
        import json
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError:
            errors.append("_meta.json is not valid JSON")

    # Check directory structure
    for subdir in ['scripts', 'references', 'assets']:
        subdir_path = skill_dir / subdir
        if subdir_path.exists() and not subdir_path.is_dir():
            errors.append(f"{subdir} exists but is not a directory")

    # Report results
    if errors:
        print("❌ VALIDATION FAILED")
        for error in errors:
            print(f"  ✗ {error}")
    if warnings:
        print("⚠ WARNINGS")
        for warning in warnings:
            print(f"  ! {warning}")

    return len(errors) == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/video-script-writer"
    else:
        skill_path = sys.argv[1]

    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)