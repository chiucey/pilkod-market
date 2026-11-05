#!/usr/bin/env python3
"""
Medical Research Analyzer Skill Validation Script
Validates skill structure and frontmatter format
"""

import os
import json
import re
from pathlib import Path

def validate_skill_structure(skill_path):
    """Validate skill directory structure"""
    issues = []
    warnings = []

    # Check required files
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_path, file)
        if not os.path.exists(file_path):
            issues.append(f"Missing required file: {file}")

    # Check directory structure
    if os.path.exists(os.path.join(skill_path, 'references')):
        warnings.append("✓ references/ directory exists")
    if os.path.exists(os.path.join(skill_path, 'scripts')):
        warnings.append("✓ scripts/ directory exists")

    return issues, warnings

def validate_frontmatter(skill_path):
    """Validate SKILL.md frontmatter format"""
    issues = []

    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    if not os.path.exists(skill_md_path):
        issues.append("SKILL.md file does not exist")
        return issues

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if frontmatter starts at first line
    if not content.startswith('---'):
        issues.append("Frontmatter must start at first line (must start with '---')")
        return issues

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False
    frontmatter_end_line = -1

    for i, line in enumerate(lines):
        if i == 0 and line.strip() == '---':
            in_frontmatter = True
            continue
        if in_frontmatter and line.strip() == '---':
            frontmatter_end_line = i
            break
        if in_frontmatter:
            frontmatter_lines.append(line)

    if frontmatter_end_line == -1:
        issues.append("Frontmatter not properly closed (missing closing '---')")
        return issues

    # Parse frontmatter
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            issues.append(f"Frontmatter missing required field: {field}")

    # Validate name format
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not re.match(r'^[a-z0-9\-]+$', name):
            issues.append(f"name field format error: '{name}', should use lowercase letters, numbers and hyphens")
        if name != os.path.basename(skill_path):
            warnings = []
            warnings.append(f"name field should match folder name (current: '{name}', folder: '{os.path.basename(skill_path)}')")

    # Validate description content
    if 'description' in frontmatter:
        desc = frontmatter['description']
        if len(desc) < 20:
            issues.append("description field content too short (recommended at least 20 characters)")
        if not any(word in desc for word in ['Medical', 'medical', 'Disease', 'disease', 'Treatment', 'treatment', 'Research', 'research', 'Drug', 'drug']):
            issues.append("description field should contain medical field related keywords")

    return issues

def validate_meta_json(skill_path):
    """Validate _meta.json format"""
    issues = []

    meta_path = os.path.join(skill_path, '_meta.json')
    if not os.path.exists(meta_path):
        issues.append("_meta.json file does not exist")
        return issues

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # Check required fields
        if 'id' not in meta:
            issues.append("_meta.json missing required field: id")
        if 'version' not in meta:
            issues.append("_meta.json missing required field: version")

        # Validate id type
        if 'id' in meta and not isinstance(meta['id'], int):
            issues.append(f"_meta.json id should be integer type, current: {type(meta['id'])}")

        # Validate version format
        if 'version' in meta:
            version = meta['version']
            if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
                issues.append(f"_meta.json version format incorrect: '{version}', should be x.y.z format")

    except json.JSONDecodeError as e:
        issues.append(f"_meta.json format error: {str(e)}")

    return issues

def main():
    skill_path = os.path.dirname(os.path.abspath(__file__)).replace('/scripts', '')

    print("=" * 60)
    print("Medical Research Analyzer - Skill Structure Validation")
    print("=" * 60)
    print()

    all_issues = []
    all_warnings = []

    # Validate structure
    print("[1/3] Validating directory structure...")
    structure_issues, structure_warnings = validate_skill_structure(skill_path)
    all_issues.extend(structure_issues)
    all_warnings.extend(structure_warnings)
    if structure_issues:
        for issue in structure_issues:
            print(f"  ✗ {issue}")
    else:
        print("  ✓ Directory structure validation passed")

    # Validate frontmatter
    print()
    print("[2/3] Validating frontmatter format...")
    frontmatter_issues = validate_frontmatter(skill_path)
    all_issues.extend(frontmatter_issues)
    if frontmatter_issues:
        for issue in frontmatter_issues:
            print(f"  ✗ {issue}")
    else:
        print("  ✓ Frontmatter format validation passed")

    # Validate _meta.json
    print()
    print("[3/3] Validating _meta.json...")
    meta_issues = validate_meta_json(skill_path)
    all_issues.extend(meta_issues)
    if meta_issues:
        for issue in meta_issues:
            print(f"  ✗ {issue}")
    else:
        print("  ✓ _meta.json validation passed")

    # Output warnings
    if all_warnings:
        print()
        print("[!] Notes:")
        for warning in all_warnings:
            print(f"  • {warning}")

    # Final result
    print()
    print("=" * 60)
    if all_issues:
        print(f"Validation Result: ✗ Failed ({len(all_issues)} issues)")
        print()
        print("Please fix the above issues and re-validate.")
        return 1
    else:
        print("Validation Result: ✓ Passed")
        print()
        print("Skill structure validation successful! Ready for packaging.")
        return 0

if __name__ == '__main__':
    exit(main())
