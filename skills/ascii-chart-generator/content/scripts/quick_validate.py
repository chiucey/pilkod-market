#!/usr/bin/env python3
"""
Quick validation script for ASCII Chart Generator skill
Checks frontmatter, structure, and basic functionality
"""

import os
import sys
import re
import json
import importlib.util

# Skill directory
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def validate_frontmatter():
    """Validate SKILL.md frontmatter"""
    print("🔍 Validating frontmatter...")

    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    if not os.path.exists(skill_md):
        print("❌ SKILL.md not found")
        return False

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter format
    if not content.startswith('---'):
        print("❌ SKILL.md must start with YAML frontmatter (---)")
        return False

    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        print("❌ Invalid frontmatter format")
        return False

    frontmatter = parts[1]

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:\s*\S', frontmatter, re.MULTILINE):
            print(f"❌ Missing required field: {field}")
            return False

    # Extract name
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        # Check name format (hyphen-case)
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
            print(f"❌ Invalid name format: {name} (use hyphen-case)")
            return False

        # Check name matches folder
        folder_name = os.path.basename(SKILL_DIR)
        if name != folder_name:
            print(f"❌ Name mismatch: '{name}' != folder name '{folder_name}'")
            return False

    print("✅ Frontmatter valid")
    return True


def validate_meta_json():
    """Validate _meta.json"""
    print("\n🔍 Validating _meta.json...")

    meta_path = os.path.join(SKILL_DIR, "_meta.json")
    if not os.path.exists(meta_path):
        print("❌ _meta.json not found")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False

    # Check required fields
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            print(f"❌ Missing required field: {field}")
            return False

    # Validate ID (should be numeric string or number)
    if not isinstance(meta['id'], (str, int)):
        print(f"❌ Invalid ID type: {type(meta['id'])}")
        return False

    # Validate version format
    version = str(meta['version'])
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print(f"❌ Invalid version format: {version} (expected x.y.z)")
        return False

    print(f"✅ _meta.json valid (id: {meta['id']}, version: {meta['version']})")
    return True


def validate_directory_structure():
    """Validate directory structure"""
    print("\n🔍 Validating directory structure...")

    required_dirs = ['scripts', 'references']
    for dir_name in required_dirs:
        dir_path = os.path.join(SKILL_DIR, dir_name)
        if not os.path.isdir(dir_path):
            print(f"❌ Missing required directory: {dir_name}")
            return False

    print("✅ Directory structure valid")
    return True


def validate_scripts():
    """Validate scripts"""
    print("\n🔍 Validating scripts...")

    # Check for core generator script
    generator_path = os.path.join(SKILL_DIR, "scripts", "generate_chart.py")
    if not os.path.exists(generator_path):
        print("❌ Missing generate_chart.py")
        return False

    # Try to import and test
    try:
        spec = importlib.util.spec_from_file_location("generate_chart", generator_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test instantiation
        gen = module.ASCIIChartGenerator()
        assert hasattr(gen, 'bar'), "Missing bar method"
        assert hasattr(gen, 'hbar'), "Missing hbar method"
        assert hasattr(gen, 'line'), "Missing line method"
        assert hasattr(gen, 'pie'), "Missing pie method"
        assert hasattr(gen, 'stacked'), "Missing stacked method"

        # Test basic generation
        result = gen.bar([10, 20, 30], ['A', 'B', 'C'])
        assert 'Bar Chart' in result or 'A' in result, "Bar chart generation failed"

        print("✅ Scripts valid and functional")
        return True

    except Exception as e:
        print(f"❌ Script validation failed: {e}")
        return False


def validate_references():
    """Validate reference files"""
    print("\n🔍 Validating reference files...")

    required_refs = ['chart_styles.md', 'color_codes.md']
    for ref_file in required_refs:
        ref_path = os.path.join(SKILL_DIR, "references", ref_file)
        if not os.path.exists(ref_path):
            print(f"❌ Missing reference: {ref_file}")
            return False

        # Check not empty
        with open(ref_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if len(content) < 50:
                print(f"❌ {ref_file} is too short or empty")
                return False

    print("✅ Reference files valid")
    return True


def main():
    """Run all validations"""
    print("=" * 50)
    print("ASCII Chart Generator - Skill Validation")
    print("=" * 50)

    results = []
    results.append(("Frontmatter", validate_frontmatter()))
    results.append(("_meta.json", validate_meta_json()))
    results.append(("Directory Structure", validate_directory_structure()))
    results.append(("Scripts", validate_scripts()))
    results.append(("References", validate_references()))

    print("\n" + "=" * 50)
    print("Validation Summary")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("🎉 All validations passed!")
        return 0
    else:
        print("⚠️  Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
