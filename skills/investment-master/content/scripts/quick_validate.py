#!/usr/bin/env python3
"""
Quick validation script for skill quality checks.
Validates SKILL.md structure and content quality.
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path):
    """Validate SKILL.md frontmatter format."""
    errors = []
    warnings = []

    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file starts with frontmatter
        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter (---)")
            return errors, warnings

        # Extract frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            errors.append("Could not parse YAML frontmatter")
            return errors, warnings

        frontmatter = frontmatter_match.group(1)

        # Check required fields
        if not re.search(r'^name:\s*.+$', frontmatter, re.MULTILINE):
            errors.append("Frontmatter must contain 'name' field")

        if not re.search(r'^description:\s*.+$', frontmatter, re.MULTILINE):
            errors.append("Frontmatter must contain 'description' field")

        # Check name format (hyphen-case)
        name_match = re.search(r'^name:\s*([a-z0-9-]+)$', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1)
            if name != name.lower():
                warnings.append("name should be lowercase with hyphens")
            if ' ' in name:
                errors.append("name should not contain spaces, use hyphens instead")

        # Check description length
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                warnings.append("description should be descriptive (at least 20 characters)")
            if len(desc) > 500:
                warnings.append("description is quite long, consider shortening")

        # Check for markdown title before frontmatter
        if re.match(r'^#\s+\w', content):
            errors.append("No markdown headers (#) should appear before frontmatter")

    except Exception as e:
        errors.append(f"Error reading SKILL.md: {str(e)}")

    return errors, warnings

def validate_meta_json(skill_dir):
    """Validate _meta.json format."""
    errors = []
    warnings = []

    meta_path = os.path.join(skill_dir, '_meta.json')
    if not os.path.exists(meta_path):
        errors.append("_meta.json file not found")
        return errors, warnings

    try:
        import json
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json must contain 'id' field")
        elif not isinstance(meta['id'], int) and not isinstance(meta['id'], str):
            errors.append("'id' should be a number or string")

        if 'version' not in meta:
            errors.append("_meta.json must contain 'version' field")
        else:
            version = meta['version']
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                warnings.append("version should follow semantic versioning (e.g., 1.0.0)")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {str(e)}")
    except Exception as e:
        errors.append(f"Error reading _meta.json: {str(e)}")

    return errors, warnings

def validate_structure(skill_dir):
    """Validate skill directory structure."""
    errors = []
    warnings = []

    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        path = os.path.join(skill_dir, filename)
        if not os.path.exists(path):
            errors.append(f"Required file '{filename}' not found")

    # Check references directory
    refs_dir = os.path.join(skill_dir, 'references')
    if os.path.exists(refs_dir):
        ref_files = list(Path(refs_dir).glob('*.md'))
        if len(ref_files) < 1:
            warnings.append("references/ directory exists but is empty")
        else:
            print(f"    Found {len(ref_files)} reference files")

    return errors, warnings

def validate_references(skill_dir):
    """Validate references are properly linked."""
    errors = []
    warnings = []

    skill_path = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_path):
        return errors, warnings

    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract references from SKILL.md
        ref_pattern = r'references/([a-zA-Z0-9-]+\.md)'
        referenced_files = re.findall(ref_pattern, content)

        refs_dir = os.path.join(skill_dir, 'references')
        if not os.path.exists(refs_dir):
            if referenced_files:
                errors.append("references/ directory not found but SKILL.md references files")
            return errors, warnings

        for ref_file in referenced_files:
            ref_path = os.path.join(refs_dir, ref_file)
            if not os.path.exists(ref_path):
                errors.append(f"Referenced file 'references/{ref_file}' not found")

    except Exception as e:
        errors.append(f"Error validating references: {str(e)}")

    return errors, warnings

def main():
    skill_dir = '/workspace/temp-skills/investment-master-multi-agent-system'

    print("=" * 60)
    print("Skill Quality Validation Report")
    print("=" * 60)
    print(f"Skill: investment-master-multi-agent")
    print(f"Directory: {skill_dir}")
    print()

    all_errors = []
    all_warnings = []

    # Run validations
    print("[1/4] Validating directory structure...")
    errors, warnings = validate_structure(skill_dir)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    if warnings:
        for w in warnings:
            print(f"    WARNING: {w}")
    print("    PASSED" if not errors else "    FAILED")
    print()

    print("[2/4] Validating frontmatter format...")
    errors, warnings = validate_frontmatter(os.path.join(skill_dir, 'SKILL.md'))
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    if warnings:
        for w in warnings:
            print(f"    WARNING: {w}")
    print("    PASSED" if not errors else "    FAILED")
    print()

    print("[3/4] Validating _meta.json...")
    errors, warnings = validate_meta_json(skill_dir)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    if warnings:
        for w in warnings:
            print(f"    WARNING: {w}")
    print("    PASSED" if not errors else "    FAILED")
    print()

    print("[4/4] Validating references...")
    errors, warnings = validate_references(skill_dir)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    if warnings:
        for w in warnings:
            print(f"    WARNING: {w}")
    print("    PASSED" if not errors else "    FAILED")
    print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total Errors: {len(all_errors)}")
    print(f"Total Warnings: {len(all_warnings)}")
    print()

    if all_errors:
        print("STATUS: FAILED - Please fix errors before packaging")
        return 1
    elif all_warnings:
        print("STATUS: PASSED with warnings")
        return 0
    else:
        print("STATUS: PASSED - All validation checks successful")
        return 0

if __name__ == '__main__':
    sys.exit(main())
