#!/usr/bin/env python3
"""
Quick validation script for skill structure
Validates frontmatter, naming, and file structure
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """Validate skill structure and frontmatter"""
    errors = []
    warnings = []

    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False

    # Read SKILL.md content
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter exists at the beginning
    if not content.startswith('---'):
        errors.append("SKILL.md must start with frontmatter (---)")
        return False

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
        return False

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            errors.append(f"Missing required frontmatter field: {field}")

    # Check name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(f"Invalid name format: {name}. Use hyphen-case (lowercase with hyphens)")
        # Check name matches folder
        expected_name = skill_path.name
        if name != expected_name:
            errors.append(f"Name mismatch: frontmatter says '{name}', folder is '{expected_name}'")

    # Check description is not empty
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 10:
            warnings.append("Description seems too short")

    # Check _meta.json exists
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        import json
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json missing 'id' field")
        if 'version' not in meta:
            errors.append("_meta.json missing 'version' field")

    # Check references directory if exists
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        ref_files = list(refs_dir.glob("*.md"))
        if len(ref_files) == 0:
            warnings.append("references/ directory exists but contains no .md files")

    # Report results
    print(f"\n{'='*60}")
    print(f"Validation Results for: {skill_path.name}")
    print(f"{'='*60}")

    if errors:
        print("\n❌ ERRORS:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    if not errors:
        print("\n✅ Validation PASSED")
        return True
    else:
        print("\n❌ Validation FAILED")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = sys.argv[1]

    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
