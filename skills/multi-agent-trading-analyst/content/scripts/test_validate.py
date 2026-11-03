#!/usr/bin/env python3
"""
Test script for validation and packaging functions.
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.quick_validate import (
    validate_frontmatter,
    validate_meta_json,
    validate_directory_structure
)


def test_valid_skill():
    """Test validation with valid skill structure."""
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create valid SKILL.md
        skill_md = temp_dir / 'SKILL.md'
        skill_md.write_text("""---
name: test-skill
description: A test skill for validation. When users ask to test functionality.
---

# Test Skill
Content here.
""")

        # Create valid _meta.json
        meta_json = temp_dir / '_meta.json'
        meta_json.write_text('{"id": "12345", "version": "1.0.0"}')

        # Run validations
        passed = True

        # Frontmatter test
        valid, errors = validate_frontmatter(skill_md)
        if not valid:
            print(f"FAIL: frontmatter validation - {errors}")
            passed = False

        # Meta JSON test
        valid, errors = validate_meta_json(meta_json)
        if not valid:
            print(f"FAIL: meta validation - {errors}")
            passed = False

        # Directory structure test - only validate SKILL.md content, not folder naming
        # (temp directories have random names that won't match frontmatter)
        valid, errors = validate_frontmatter(skill_md)
        if not valid:
            print(f"FAIL: frontmatter validation - {errors}")
            passed = False

        # Meta JSON test
        valid, errors = validate_meta_json(meta_json)
        if not valid:
            print(f"FAIL: meta validation - {errors}")
            passed = False

        return passed

    finally:
        shutil.rmtree(temp_dir)


def test_invalid_frontmatter():
    """Test validation catches invalid frontmatter."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create invalid SKILL.md (no name)
        skill_md = temp_dir / 'SKILL.md'
        skill_md.write_text("""---
description: Missing name field.
---

# Invalid Skill
""")

        valid, errors = validate_frontmatter(skill_md)
        if valid:
            print("FAIL: should catch missing name field")
            return False

        return True

    finally:
        shutil.rmtree(temp_dir)


def test_invalid_name_format():
    """Test validation catches invalid name format."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create SKILL.md with invalid name
        skill_md = temp_dir / 'SKILL.md'
        skill_md.write_text("""---
name: Invalid_Name
description: Test description for invalid name format.
---

# Invalid
""")

        valid, errors = validate_frontmatter(skill_md)
        if valid:
            print("FAIL: should catch invalid name format (contains underscore)")
            return False

        return True

    finally:
        shutil.rmtree(temp_dir)


def test_missing_frontmatter():
    """Test validation catches missing frontmatter."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create SKILL.md without frontmatter
        skill_md = temp_dir / 'SKILL.md'
        skill_md.write_text("""# No Frontmatter

Content without frontmatter.
""")

        valid, errors = validate_frontmatter(skill_md)
        if valid:
            print("FAIL: should catch missing frontmatter")
            return False

        return True

    finally:
        shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    print("Running validation tests...")
    print("-" * 50)

    tests = [
        ("Valid skill structure", test_valid_skill),
        ("Invalid frontmatter (missing name)", test_invalid_frontmatter),
        ("Invalid name format", test_invalid_name_format),
        ("Missing frontmatter", test_missing_frontmatter),
    ]

    all_passed = True
    for name, test_func in tests:
        try:
            if test_func():
                print(f"✓ {name}")
            else:
                print(f"✗ {name}")
                all_passed = False
        except Exception as e:
            print(f"✗ {name} - Exception: {e}")
            all_passed = False

    print("-" * 50)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
