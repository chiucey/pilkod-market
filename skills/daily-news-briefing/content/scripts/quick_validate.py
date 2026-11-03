#!/usr/bin/env python3
"""
Quick validation script for daily-news-briefing skill
Checks frontmatter format, required fields, and structure integrity
"""

import os
import re
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path: str) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format and required fields"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with ---
    if not content.strip().startswith('---'):
        errors.append("❌ SKILL.md must start with frontmatter (---)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("❌ Cannot parse frontmatter block")
        return False, errors

    frontmatter_text = frontmatter_match.group(1)

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:\s*.+', frontmatter_text, re.MULTILINE):
            errors.append(f"❌ Missing required frontmatter field: {field}")

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(f"❌ name '{name}' must use hyphen-case format (e.g., daily-news-briefing)")
        if len(name) > 64:
            errors.append(f"❌ name length exceeds 64 characters")

    # Validate description contains trigger phrases
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        description = desc_match.group(1).strip()
        trigger_phrases = ['晨读简报', '每日新闻', 'morning briefing', '新闻英语学习', 'daily news']
        has_trigger = any(phrase.lower() in description.lower() for phrase in trigger_phrases)
        if not has_trigger:
            errors.append("⚠️ description should include trigger phrases like '晨读简报', 'morning briefing'")

    return len(errors) == 0, errors


def validate_meta_json(meta_path: str) -> tuple[bool, list[str]]:
    """Validate _meta.json structure"""
    errors = []

    if not os.path.exists(meta_path):
        errors.append("❌ _meta.json not found")
        return False, errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"❌ _meta.json is not valid JSON: {e}")
        return False, errors

    # Check required fields
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"❌ _meta.json missing required field: {field}")

    # Validate version format (semver)
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"❌ version '{version}' must follow semver format (e.g., 1.0.0)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_dir: str) -> tuple[bool, list[str]]:
    """Validate skill directory structure"""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            errors.append(f"❌ Missing required file: {file}")

    # Check for forbidden files (secrets, credentials)
    forbidden_patterns = ['.env', 'credentials', 'secrets', 'id_rsa', '.pem']
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            if any(pattern in file.lower() for pattern in forbidden_patterns):
                errors.append(f"❌ Forbidden file detected: {file}")

    return len(errors) == 0, errors


def main():
    skill_dir = "/workspace/temp-skills/daily-news-briefing"
    all_passed = True

    print("=" * 50)
    print("🔍 Daily News Briefing - Skill Validation")
    print("=" * 50)

    # Validate frontmatter
    print("\n📋 Checking SKILL.md frontmatter...")
    passed, errors = validate_frontmatter(os.path.join(skill_dir, 'SKILL.md'))
    if passed:
        print("   ✅ Frontmatter validation passed")
    else:
        for error in errors:
            print(f"   {error}")
        all_passed = False

    # Validate meta.json
    print("\n📋 Checking _meta.json...")
    passed, errors = validate_meta_json(os.path.join(skill_dir, '_meta.json'))
    if passed:
        print("   ✅ _meta.json validation passed")
    else:
        for error in errors:
            print(f"   {error}")
        all_passed = False

    # Validate directory structure
    print("\n📋 Checking directory structure...")
    passed, errors = validate_directory_structure(skill_dir)
    if passed:
        print("   ✅ Directory structure validation passed")
    else:
        for error in errors:
            print(f"   {error}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All validations passed!")
        return 0
    else:
        print("❌ Some validations failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
