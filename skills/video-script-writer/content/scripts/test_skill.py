#!/usr/bin/env python3
"""
Test script for skill validation and packaging
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from quick_validate import validate_skill
from package_skill import package_skill

def run_tests():
    """Run all tests for the skill"""
    skill_path = "/workspace/temp-skills/video-script-writer"
    all_passed = True

    print("=" * 50)
    print("Running Skill Tests")
    print("=" * 50)

    # Test 1: Validation
    print("\n[1/3] Testing validation...")
    if validate_skill(skill_path):
        print("✓ Validation passed")
    else:
        print("✗ Validation failed")
        all_passed = False

    # Test 2: Package creation
    print("\n[2/3] Testing packaging...")
    try:
        output_file = package_skill(skill_path)
        if Path(output_file).exists():
            print(f"✓ Package created: {output_file}")
            # Clean up test package
            Path(output_file).unlink()
        else:
            print("✗ Package file not created")
            all_passed = False
    except Exception as e:
        print(f"✗ Packaging failed: {e}")
        all_passed = False

    # Test 3: Frontmatter check
    print("\n[3/3] Testing frontmatter format...")
    skill_md = Path(skill_path) / "SKILL.md"
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    if content.startswith('---'):
        frontmatter_end = content.find('---', 3)
        if frontmatter_end != -1:
            fm = content[3:frontmatter_end]
            if 'name:' in fm and 'description:' in fm:
                print("✓ Frontmatter format correct")
            else:
                print("✗ Frontmatter missing required fields")
                all_passed = False
        else:
            print("✗ Frontmatter not properly closed")
            all_passed = False
    else:
        print("✗ SKILL.md must start with ---")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 50)

    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)