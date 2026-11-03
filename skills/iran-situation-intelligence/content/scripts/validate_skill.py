#!/usr/bin/env python3
"""
Iran Situation Intelligence Skill Validation Script
Validates structural integrity of SKILL.md and _meta.json
"""

import os
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """Validate frontmatter of SKILL.md"""
    errors = []
    warnings = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if starts with ---
    if not content.strip().startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return errors, warnings

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not any(line.strip().startswith(f'{field}:') for line in frontmatter_lines):
            errors.append(f"Missing required field: {field}")

    # Check name field format
    name_match = [line for line in frontmatter_lines if line.strip().startswith('name:')]
    if name_match:
        name_value = name_match[0].split(':', 1)[1].strip()
        if not name_value:
            errors.append("name field cannot be empty")
        elif ' ' in name_value:
            warnings.append("name field should use hyphen format (e.g., iran-situation-intelligence)")

    # Check description field
    desc_match = [line for line in frontmatter_lines if line.strip().startswith('description:')]
    if desc_match:
        desc_value = desc_match[0].split(':', 1)[1].strip()
        if len(desc_value) < 20:
            warnings.append("description should be at least 20 characters for accurate triggering")
        if 'Use when' not in desc_value and '触发' not in desc_value:
            warnings.append("description should include trigger phrases (e.g., 'Use when...' or '触发短语：')")

    # Check frontmatter structure: should have two --- delimiters
    dash_count = content.split('\n')[0:20].count('---')
    if dash_count < 2:
        errors.append("frontmatter must be properly delimited by --- (start and end)")

    # Extract content after frontmatter
    parts = content.split('---')
    if len(parts) >= 3:
        markdown_content = ''.join(parts[2:]).strip()

    return errors, warnings


def validate_meta_json(meta_path):
    """Validate _meta.json structure"""
    errors = []
    warnings = []

    if not os.path.exists(meta_path):
        errors.append("_meta.json file does not exist")
        return errors, warnings

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON format error: {e}")
        return errors, warnings

    # Check required fields
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required field: {field}")

    # Validate id
    if 'id' in meta:
        if not isinstance(meta['id'], int):
            errors.append("id must be an integer")
        elif meta['id'] <= 0:
            errors.append("id must be a positive integer")

    # Validate version
    if 'version' in meta:
        version = meta['version']
        if not isinstance(version, str):
            errors.append("version must be a string (e.g., '1.0.0')")
        elif not version.replace('.', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', ''):
            parts = version.split('.')
            if len(parts) != 3:
                errors.append("version format should be 'major.minor.patch' (e.g., '1.0.0')")

    return errors, warnings


def validate_directory_structure(skill_dir):
    """Validate directory structure"""
    errors = []
    warnings = []

    # Check required files
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            errors.append(f"Missing required file: {file}")

    # Check optional directories
    optional_dirs = ['references', 'scripts', 'assets']
    for dir_name in optional_dirs:
        dir_path = os.path.join(skill_dir, dir_name)
        if os.path.exists(dir_path):
            if dir_name == 'references':
                ref_files = os.listdir(dir_path)
                if not ref_files:
                    warnings.append("references directory is empty, consider adding reference materials")

    return errors, warnings


def validate_content_quality(skill_md_path):
    """Validate SKILL.md content quality"""
    errors = []
    warnings = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for key workflow sections
    key_sections = [
        'workflow',
        'source',
        'output',
        'quality'
    ]

    for section in key_sections:
        if section not in content.lower():
            warnings.append(f"Consider including guidance related to '{section}'")

    # Check for specific tool calls
    if 'batch_web_search' not in content and 'extract_content' not in content:
        warnings.append("Consider including specific tool call examples")

    # Check for information source priority
    if '一级' not in content and 'tier1' not in content.lower():
        warnings.append("Consider including information source priority hierarchy")

    return errors, warnings


def main():
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    if 'scripts' in skill_dir:
        skill_dir = os.path.dirname(skill_dir)

    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    meta_path = os.path.join(skill_dir, '_meta.json')

    all_errors = []
    all_warnings = []

    print("=" * 60)
    print("Iran Situation Intelligence Skill - Validation Check")
    print("=" * 60)

    # 1. Frontmatter validation
    print("\n[1/4] Validating frontmatter structure...")
    errors, warnings = validate_frontmatter(skill_md_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"   [ERROR] {e}")
    if warnings:
        for w in warnings:
            print(f"   [WARN] {w}")
    if not errors and not warnings:
        print("   [OK] Frontmatter structure is correct")

    # 2. Meta JSON validation
    print("\n[2/4] Validating _meta.json...")
    errors, warnings = validate_meta_json(meta_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"   [ERROR] {e}")
    if warnings:
        for w in warnings:
            print(f"   [WARN] {w}")
    if not errors and not warnings:
        print("   [OK] _meta.json structure is correct")

    # 3. Directory structure validation
    print("\n[3/4] Validating directory structure...")
    errors, warnings = validate_directory_structure(skill_dir)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"   [ERROR] {e}")
    if warnings:
        for w in warnings:
            print(f"   [WARN] {w}")
    if not errors and not warnings:
        print("   [OK] Directory structure is complete")

    # 4. Content quality validation
    print("\n[4/4] Validating content quality...")
    errors, warnings = validate_content_quality(skill_md_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"   [ERROR] {e}")
    if warnings:
        for w in warnings:
            print(f"   [WARN] {w}")
    if not errors and not warnings:
        print("   [OK] Content quality meets standards")

    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    print(f"Errors: {len(all_errors)}")
    print(f"Warnings: {len(all_warnings)}")

    if all_errors:
        print("\n[FAIL] Validation failed - please fix the errors above")
        return 1
    elif all_warnings:
        print("\n[WARN] Validation passed with warnings - consider optimization")
        return 0
    else:
        print("\n[OK] Validation fully passed")
        return 0


if __name__ == '__main__':
    sys.exit(main())
