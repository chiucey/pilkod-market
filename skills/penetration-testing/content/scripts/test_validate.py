#!/usr/bin/env python3
"""
Test suite for Penetration Testing Skill validation scripts.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.quick_validate import validate_skill

def test_valid_skill():
    """Test validation of a properly structured skill."""
    # Use the actual skill directory
    skill_path = "/workspace/temp-skills/penetration-testing"
    result = validate_skill(skill_path)
    assert result, "Valid skill should pass validation"
    print("[PASS] test_valid_skill")

def test_missing_skill_md():
    """Test validation fails when SKILL.md is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_skill = Path(tmpdir) / "test-skill"
        tmp_skill.mkdir()

        # Don't create SKILL.md
        _meta = tmp_skill / "_meta.json"
        _meta.write_text('{"id": "test", "version": "1.0.0"}')

        result = validate_skill(str(tmp_skill))
        assert not result, "Missing SKILL.md should fail validation"
    print("[PASS] test_missing_skill_md")

def test_missing_meta():
    """Test validation fails when _meta.json is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_skill = Path(tmpdir) / "test-skill"
        tmp_skill.mkdir()

        skill_md = tmp_skill / "SKILL.md"
        skill_md.write_text("---\nname: test\ndescription: Test\n---\n# Test")

        result = validate_skill(str(tmp_skill))
        assert not result, "Missing _meta.json should fail validation"
    print("[PASS] test_missing_meta")

def test_invalid_frontmatter():
    """Test validation fails with invalid frontmatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_skill = Path(tmpdir) / "test-skill"
        tmp_skill.mkdir()

        skill_md = tmp_skill / "SKILL.md"
        skill_md.write_text("# Invalid - no frontmatter\nContent")

        _meta = tmp_skill / "_meta.json"
        _meta.write_text('{"id": "test", "version": "1.0.0"}')

        result = validate_skill(str(tmp_skill))
        assert not result, "Invalid frontmatter should fail validation"
    print("[PASS] test_invalid_frontmatter")

def run_all_tests():
    """Run all validation tests."""
    print("=" * 60)
    print("RUNNING VALIDATION TESTS")
    print("=" * 60)

    tests = [
        test_valid_skill,
        test_missing_skill_md,
        test_missing_meta,
        test_invalid_frontmatter,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
