#!/usr/bin/env python3
"""
Quick validation script for legal-case-searcher skill.
Validates SKILL.md structure and frontmatter requirements.
"""

import json
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path: str) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter and structure."""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check 1: Frontmatter must be at the start
    if not content.startswith('---'):
        errors.append("❌ SKILL.md must start with frontmatter delimiter '---'")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("❌ Cannot parse frontmatter block")
        return False, errors

    frontmatter_text = frontmatter_match.group(1)

    # Parse YAML-like frontmatter
    required_keys = ['name', 'description']
    for key in required_keys:
        if not re.search(rf'^{key}:', frontmatter_text, re.MULTILINE):
            errors.append(f"❌ Missing required frontmatter key: '{key}'")

    # Check name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name_value):
            errors.append(f"❌ 'name' should be hyphen-case, got: '{name_value}'")
        # Check folder name match
        folder_name = Path(skill_md_path).parent.name
        if name_value != folder_name:
            errors.append(f"⚠️ 'name' ({name_value}) differs from folder name ({folder_name})")

    # Check description contains trigger phrases
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            errors.append("⚠️ 'description' seems too short, should include trigger phrases")
        if '当用户' not in desc_value and 'when' not in desc_value.lower():
            errors.append("⚠️ 'description' should include trigger context like '当用户...'")

    return len(errors) == 0, errors


def validate_meta_json(meta_path: str) -> tuple[bool, list[str]]:
    """Validate _meta.json structure."""
    errors = []

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_keys = ['id', 'version']
    for key in required_keys:
        if key not in meta:
            errors.append(f"❌ Missing required key in _meta.json: '{key}'")

    # Validate version format (semantic versioning)
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"❌ 'version' should be semantic format (x.y.z), got: '{version}'")

    return len(errors) == 0, errors


def validate_directory_structure(skill_dir: str) -> tuple[bool, list[str]]:
    """Validate skill directory structure."""
    errors = []

    skill_path = Path(skill_dir)

    # Check required files exist
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        file_path = skill_path / filename
        if not file_path.exists():
            errors.append(f"❌ Missing required file: {filename}")

    # Check optional directories exist
    optional_dirs = ['scripts', 'references', 'assets']
    for dirname in optional_dirs:
        dir_path = skill_path / dirname
        if dir_path.exists() and not dir_path.is_dir():
            errors.append(f"⚠️ {dirname} exists but is not a directory")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    skill_dir = sys.argv[1]
    all_errors = []

    # Check directory structure
    struct_ok, struct_errors = validate_directory_structure(skill_dir)
    all_errors.extend(struct_errors)

    # Check SKILL.md
    skill_md = Path(skill_dir) / 'SKILL.md'
    if skill_md.exists():
        fm_ok, fm_errors = validate_frontmatter(str(skill_md))
        all_errors.extend(fm_errors)
    else:
        all_errors.append("❌ SKILL.md not found")

    # Check _meta.json
    meta_json = Path(skill_dir) / '_meta.json'
    if meta_json.exists():
        meta_ok, meta_errors = validate_meta_json(str(meta_json))
        all_errors.extend(meta_errors)

    # Report
    print("=" * 50)
    print("Skill Validation Report")
    print("=" * 50)

    if all_errors:
        for err in all_errors:
            print(err)
        print("\n❌ Validation FAILED")
        sys.exit(1)
    else:
        print("✅ All validation checks passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
