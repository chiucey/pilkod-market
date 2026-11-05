#!/usr/bin/env python3
"""
Skill Validation Script - Validates paper-grading-assistant skill structure and content
"""

import os
import json
import re
import sys
from pathlib import Path

# Skill root directory
SKILL_ROOT = Path(__file__).parent.parent

# Required files list
REQUIRED_FILES = [
    "SKILL.md",
    "_meta.json"
]

# Required frontmatter fields
REQUIRED_FRONTMATTER_FIELDS = [
    "name",
    "description"
]

# Required _meta.json fields
REQUIRED_META_FIELDS = [
    "id",
    "version"
]


def check_file_exists():
    """Check if required files exist"""
    print("=" * 60)
    print("1. Checking file structure...")
    print("=" * 60)

    all_exist = True
    for file_name in REQUIRED_FILES:
        file_path = SKILL_ROOT / file_name
        if file_path.exists():
            print(f"  ✓ {file_name} exists")
        else:
            print(f"  ✗ {file_name} missing")
            all_exist = False

    return all_exist


def check_frontmatter():
    """Check SKILL.md frontmatter format"""
    print("\n" + "=" * 60)
    print("2. Checking Frontmatter format...")
    print("=" * 60)

    skill_md = SKILL_ROOT / "SKILL.md"
    if not skill_md.exists():
        print("  ✗ SKILL.md does not exist")
        return False

    content = skill_md.read_text(encoding='utf-8')

    # Check if file starts with frontmatter
    if not content.strip().startswith('---'):
        print("  ✗ SKILL.md must start with YAML frontmatter")
        print("    Error: First line should be '---'")
        return False

    # Extract frontmatter
    lines = content.split('\n')
    if len(lines) < 3:
        print("  ✗ Frontmatter format incorrect, needs at least 3 lines")
        return False

    # Find frontmatter end marker
    end_index = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_index = i
            break

    if end_index == -1:
        print("  ✗ Missing frontmatter end marker '---'")
        return False

    # Parse frontmatter
    frontmatter_lines = lines[1:end_index]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Check required fields
    all_fields_present = True
    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field in frontmatter:
            print(f"  ✓ {field}: {frontmatter[field][:50]}...")
        else:
            print(f"  ✗ Missing required field: {field}")
            all_fields_present = False

    # Check if name field matches folder name
    skill_folder_name = SKILL_ROOT.name
    if 'name' in frontmatter:
        skill_name = frontmatter['name'].replace(' ', '-').lower()
        if skill_name != skill_folder_name.lower():
            print(f"  ⚠ Warning: name field '{frontmatter['name']}' may not match folder name '{skill_folder_name}'")

    return all_fields_present


def check_meta_json():
    """Check _meta.json format and content"""
    print("\n" + "=" * 60)
    print("3. Checking _meta.json format...")
    print("=" * 60)

    meta_file = SKILL_ROOT / "_meta.json"
    if not meta_file.exists():
        print("  ✗ _meta.json does not exist")
        return False

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON format error: {e}")
        return False

    # Check required fields
    all_fields_present = True
    for field in REQUIRED_META_FIELDS:
        if field in meta:
            print(f"  ✓ {field}: {meta[field]}")
        else:
            print(f"  ✗ Missing required field: {field}")
            all_fields_present = False

    # Check version format
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            print(f"  ⚠ Warning: version '{version}' should use semantic versioning (e.g., 1.0.0)")

    return all_fields_present


def check_description_quality():
    """Check if description contains trigger phrases"""
    print("\n" + "=" * 60)
    print("4. Checking trigger phrases...")
    print("=" * 60)

    skill_md = SKILL_ROOT / "SKILL.md"
    content = skill_md.read_text(encoding='utf-8')

    # Extract frontmatter
    lines = content.split('\n')
    end_index = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_index = i
            break

    frontmatter_lines = lines[1:end_index]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    description = frontmatter.get('description', '')

    # Suggested trigger keyword list
    suggested_keywords = ['grading', 'paper', 'assignment', 'review', 'evaluation', 'Word', 'annotation']

    found_keywords = []
    missing_keywords = []

    for keyword in suggested_keywords:
        if keyword.lower() in description.lower():
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    if found_keywords:
        print(f"  ✓ Found trigger keywords: {', '.join(found_keywords)}")

    if missing_keywords:
        print(f"  ⚠ Suggest adding trigger keywords: {', '.join(missing_keywords)}")

    return True


def check_content_quality():
    """Check SKILL.md content quality"""
    print("\n" + "=" * 60)
    print("5. Checking content quality...")
    print("=" * 60)

    skill_md = SKILL_ROOT / "SKILL.md"
    content = skill_md.read_text(encoding='utf-8')

    # Check basic structure
    required_sections = [
        'Core Functions',
        'Trigger Scenarios',
        'Workflow',
        'Output Requirements'
    ]

    all_sections_present = True
    for section in required_sections:
        if section in content:
            print(f"  ✓ Contains section: {section}")
        else:
            print(f"  ✗ Missing section: {section}")
            all_sections_present = False

    # Check if content is substantial enough
    content_lines = [line for line in content.split('\n') if line.strip()]
    if len(content_lines) < 50:
        print(f"  ⚠ Warning: Content may be too brief ({len(content_lines)} lines)")
    else:
        print(f"  ✓ Substantial content ({len(content_lines)} lines)")

    return all_sections_present


def main():
    """Main function - run all checks"""
    print("\n" + "=" * 60)
    print("Paper Grading Assistant - Skill Validation")
    print("=" * 60)
    print(f"\nSkill directory: {SKILL_ROOT}")
    print()

    results = {
        'file_exists': check_file_exists(),
        'frontmatter': check_frontmatter(),
        'meta_json': check_meta_json(),
        'description_quality': check_description_quality(),
        'content_quality': check_content_quality()
    }

    # Summary results
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    all_passed = True
    for check_name, passed in results.items():
        status = "✓ Pass" if passed else "✗ Fail"
        print(f"  {check_name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All validations passed! Skill structure is correct.")
        print("=" * 60)
        return 0
    else:
        print("✗ Some validations failed, please fix and retry.")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
