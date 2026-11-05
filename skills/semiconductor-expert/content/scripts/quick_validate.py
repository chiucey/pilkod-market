#!/usr/bin/env python3
"""
Quick validation script for semiconductor-expert skill.
Validates frontmatter, structure, and naming conventions.
"""

import os
import sys
import json
import re
from pathlib import Path


def validate_frontmatter(skill_md_path):
    """Validate SKILL.md frontmatter format and content."""
    errors = []
    warnings = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter is at the beginning
    if not content.startswith('---'):
        errors.append("SKILL.md must start with frontmatter (---)")
        return errors, warnings

    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append("Frontmatter must be closed with ---")
        return errors, warnings

    frontmatter = parts[1]

    # Check required fields
    if 'name:' not in frontmatter:
        errors.append("Frontmatter must contain 'name' field")

    if 'description:' not in frontmatter:
        errors.append("Frontmatter must contain 'description' field")

    # Extract name
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        # Check name is hyphen-case
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            warnings.append(f"Name '{name}' should use hyphen-case format")
        # Check name matches folder name
        folder_name = Path(skill_md_path).parent.name
        if name != folder_name:
            errors.append(f"Name '{name}' must match folder name '{folder_name}'")

    # Check description contains trigger phrases
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            warnings.append("Description should be descriptive (>= 20 chars)")
        if '?' not in desc and 'when' not in desc.lower():
            warnings.append("Description should contain trigger phrases like 'when users ask'")

    return errors, warnings


def validate_meta_json(skill_dir):
    """Validate _meta.json exists and has required fields."""
    errors = []
    warnings = []

    meta_path = skill_dir / '_meta.json'
    if not meta_path.exists():
        errors.append("_meta.json does not exist")
        return errors, warnings

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json is invalid JSON: {e}")
        return errors, warnings

    # Check required fields
    if 'id' not in meta:
        errors.append("_meta.json must contain 'id' field")
    elif not isinstance(meta['id'], str) and not isinstance(meta['id'], int):
        errors.append("_meta.json 'id' must be a string or integer")

    if 'version' not in meta:
        errors.append("_meta.json must contain 'version' field")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta.get('version', '')):
        warnings.append("Version should follow semantic versioning (x.y.z)")

    return errors, warnings


def validate_directory_structure(skill_dir):
    """Validate directory structure follows conventions."""
    errors = []
    warnings = []

    # Check required files exist
    if not (skill_dir / 'SKILL.md').exists():
        errors.append("SKILL.md does not exist")

    # Check for any non-ASCII paths
    for root, dirs, files in os.walk(skill_dir):
        for name in files + dirs:
            if not name.isascii():
                errors.append(f"Non-ASCII path found: {os.path.join(root, name)}")
                break

    return errors, warnings


def validate_naming(skill_dir):
    """Validate naming conventions."""
    errors = []
    warnings = []

    folder_name = skill_dir.name

    # Check folder name is hyphen-case and ASCII
    if not folder_name.isascii():
        errors.append(f"Folder name '{folder_name}' contains non-ASCII characters")

    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', folder_name):
        errors.append(f"Folder name '{folder_name}' should use hyphen-case format")

    if len(folder_name) > 64:
        errors.append(f"Folder name exceeds 64 characters ({len(folder_name)})")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1]).resolve()

    if not skill_dir.exists():
        print(f"Error: Directory {skill_dir} does not exist")
        sys.exit(1)

    all_errors = []
    all_warnings = []

    # Run all validations
    skill_md = skill_dir / 'SKILL.md'
    if skill_md.exists():
        errors, warnings = validate_frontmatter(skill_md)
        all_errors.extend([f"Frontmatter: {e}" for e in errors])
        all_warnings.extend([f"Frontmatter: {w}" for w in warnings])

    errors, warnings = validate_meta_json(skill_dir)
    all_errors.extend([f"_meta.json: {e}" for e in errors])
    all_warnings.extend([f"_meta.json: {w}" for w in warnings])

    errors, warnings = validate_directory_structure(skill_dir)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = validate_naming(skill_dir)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Output results
    print(f"\n{'='*60}")
    print(f"Validation Report: {skill_dir.name}")
    print(f"{'='*60}")

    if all_warnings:
        print(f"\nWarnings ({len(all_warnings)}):")
        for w in all_warnings:
            print(f"  ⚠️  {w}")

    if all_errors:
        print(f"\nErrors ({len(all_errors)}):")
        for e in all_errors:
            print(f"  ❌ {e}")
        print(f"\n❌ Validation FAILED")
        sys.exit(1)
    else:
        print(f"\n✅ Validation PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
