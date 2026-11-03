#!/usr/bin/env python3
"""
Quick validation script for senior-designer-promotion-report skill.
Validates frontmatter, structure, and naming conventions.
"""

import os
import sys
import json
import re
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> list:
    """Validate SKILL.md frontmatter is at the beginning."""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return errors

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter is at the beginning
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid YAML frontmatter format")
        return errors

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            errors.append(f"Missing required frontmatter field: {field}")

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(f"Name '{name}' should be hyphen-case (e.g., 'my-skill')")
        if ' ' in name:
            errors.append(f"Name '{name}' should not contain spaces")

    # Validate description contains trigger phrase
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append("Description should be at least 20 characters")
        if '当' not in desc and 'use when' not in desc.lower():
            errors.append("Description should contain trigger phrases (e.g., '当用户要求...')")

    return errors

def validate_meta_json(skill_path: Path) -> list:
    """Validate _meta.json structure."""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        errors.append("_meta.json not found")
        return errors

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json is not valid JSON: {e}")
        return errors

    # Check required fields
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required _meta.json field: {field}")

    # Validate id is integer
    if 'id' in meta and not isinstance(meta['id'], int):
        errors.append("_meta.json 'id' must be an integer")

    # Validate version format (semantic versioning)
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"Version '{version}' should follow semantic versioning (e.g., '1.0.0')")

    return errors

def validate_directory_structure(skill_path: Path) -> list:
    """Validate skill directory structure."""
    errors = []

    # Skill name should match directory name
    skill_name = skill_path.name

    # Check SKILL.md exists
    if not (skill_path / "SKILL.md").exists():
        errors.append("SKILL.md must exist in skill root")

    # Check references directory (if exists, should have content)
    references_dir = skill_path / "references"
    if references_dir.exists():
        ref_files = list(references_dir.glob("*.md"))
        if len(ref_files) == 0:
            errors.append("references/ directory exists but contains no .md files")

    return errors

def main():
    """Main validation function."""
    # Get skill path from command line or use default
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        # Assume running from skill directory or parent
        skill_path = Path(__file__).parent.parent

    print(f"Validating skill: {skill_path}")
    print("-" * 50)

    all_errors = []

    # Run validations
    all_errors.extend(validate_frontmatter(skill_path))
    all_errors.extend(validate_meta_json(skill_path))
    all_errors.extend(validate_directory_structure(skill_path))

    # Report results
    if all_errors:
        print("❌ Validation FAILED:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Frontmatter validation passed")
        print("✓ _meta.json validation passed")
        print("✓ Directory structure validation passed")
        print("\n✅ All validations passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
