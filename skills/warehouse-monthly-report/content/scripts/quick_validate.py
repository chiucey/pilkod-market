#!/usr/bin/env python3
"""
Quick Validation Script for Warehouse Monthly Report Skill
Validates SKILL.md frontmatter, structure, and required files
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path: str) -> tuple[bool, list[str]]:
    """Validate frontmatter structure and required fields"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with ---
    if not content.startswith('---'):
        errors.append("❌ SKILL.md must start with frontmatter delimiter '---'")
        return False, errors

    # Extract frontmatter
    frontmatter_end = content.find('\n---', 3)
    if frontmatter_end == -1:
        errors.append("❌ Missing closing '---' for frontmatter")
        return False, errors

    frontmatter_text = content[3:frontmatter_end].strip()

    # Check for required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        pattern = rf'^{field}:'
        if not re.search(pattern, frontmatter_text, re.MULTILINE):
            errors.append(f"❌ Missing required frontmatter field: '{field}'")

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(f"❌ 'name' must be hyphen-case: got '{name}'")

    # Check for markdown title before frontmatter
    if re.search(r'^#\s+\w', content[:frontmatter_end + 3], re.MULTILINE):
        errors.append("❌ Markdown title (#) must NOT appear before frontmatter")

    # Check description has trigger phrase
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if 'Use when' not in desc and '当用户' not in desc:
            errors.append("⚠️  description should include trigger phrase like 'Use when...' or '当用户'")

    return len(errors) == 0, errors


def validate_meta_json(meta_path: str) -> tuple[bool, list[str]]:
    """Validate _meta.json structure"""
    errors = []

    if not os.path.exists(meta_path):
        errors.append("❌ Missing _meta.json file")
        return False, errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"❌ _meta.json is not valid JSON: {e}")
        return False, errors

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"❌ Missing required _meta.json field: '{field}'")

    # Validate version format (semantic versioning)
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"❌ 'version' must be semantic (x.y.z): got '{version}'")

    return len(errors) == 0, errors


def validate_directory_structure(skill_dir: str) -> tuple[bool, list[str]]:
    """Validate directory structure and naming"""
    errors = []

    # Check skill name matches directory name
    skill_name = os.path.basename(skill_dir.rstrip('/'))
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        errors.append(f"❌ Directory name must be lowercase hyphen-case: got '{skill_name}'")

    # Check for required files
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = os.path.join(skill_dir, filename)
        if not os.path.exists(filepath):
            errors.append(f"❌ Missing required file: {filename}")

    return len(errors) == 0, errors


def validate_references(skill_dir: str) -> tuple[bool, list[str]]:
    """Validate references directory if exists"""
    warnings = []
    references_dir = os.path.join(skill_dir, 'references')

    if not os.path.exists(references_dir):
        return True, []

    # Check for meaningful reference files
    ref_files = list(Path(references_dir).glob('*.md'))
    if len(ref_files) == 0:
        warnings.append("⚠️  references/ exists but contains no .md files")

    return True, warnings


def run_validation(skill_path: str) -> bool:
    """Run all validations"""
    print("=" * 50)
    print("🎯 Skill Validation Report")
    print("=" * 50)
    print(f"📁 Skill Path: {skill_path}\n")

    all_errors = []
    all_warnings = []

    # 1. Frontmatter validation
    print("📋 Checking frontmatter structure...")
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md):
        valid, errors = validate_frontmatter(skill_md)
        all_errors.extend(errors)
        if valid:
            print("   ✅ Frontmatter structure OK")
    else:
        all_errors.append("❌ SKILL.md not found")
        print("   ❌ SKILL.md not found")
    print()

    # 2. Meta JSON validation
    print("📋 Checking _meta.json...")
    meta_json = os.path.join(skill_path, '_meta.json')
    valid, errors = validate_meta_json(meta_json)
    all_errors.extend(errors)
    if valid:
        print("   ✅ _meta.json structure OK")
    print()

    # 3. Directory structure validation
    print("📋 Checking directory structure...")
    valid, errors = validate_directory_structure(skill_path)
    all_errors.extend(errors)
    if valid:
        print("   ✅ Directory structure OK")
    print()

    # 4. References validation
    print("📋 Checking references...")
    valid, warnings = validate_references(skill_path)
    all_warnings.extend(warnings)
    if valid and not warnings:
        print("   ✅ References check OK (no references needed)")
    elif warnings:
        for w in warnings:
            print(f"   {w}")
    print()

    # Final report
    print("=" * 50)
    if all_errors:
        print(f"❌ VALIDATION FAILED: {len(all_errors)} error(s)")
        for err in all_errors:
            print(f"   {err}")
        return False
    else:
        print("✅ ALL VALIDATIONS PASSED")
        if all_warnings:
            print(f"📝 {len(all_warnings)} warning(s):")
            for w in all_warnings:
                print(f"   {w}")
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Default to current directory
        skill_path = os.path.dirname(os.path.abspath(__file__))
        skill_path = os.path.dirname(skill_path)  # Go up one level
    else:
        skill_path = sys.argv[1]

    success = run_validation(skill_path)
    sys.exit(0 if success else 1)
