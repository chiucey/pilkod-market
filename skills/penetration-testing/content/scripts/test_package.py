#!/usr/bin/env python3
"""
Test suite for Penetration Testing Skill packaging.
"""

import os
import sys
import tempfile
import json
import zipfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.package_skill import package_skill, verify_package

def test_package_creation():
    """Test creating a skill package."""
    skill_path = "/workspace/temp-skills/penetration-testing"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = package_skill(skill_path, tmpdir)

        assert Path(output_path).exists(), "Package file should exist"
        assert output_path.endswith('.skill'), "Package should have .skill extension"

        # Verify package contents
        assert verify_package(output_path), "Package verification should pass"

        print(f"[PASS] test_package_creation: {output_path}")

def test_package_structure():
    """Test that package contains expected files."""
    skill_path = "/workspace/temp-skills/penetration-testing"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = package_skill(skill_path, tmpdir)

        with zipfile.ZipFile(output_path, 'r') as zf:
            contents = set(zf.namelist())

            required = {'SKILL.md', '_meta.json', 'references/pentest-checklist.md'}
            for req in required:
                assert req in contents, f"Package should contain {req}"

        print("[PASS] test_package_structure")

def run_all_tests():
    """Run all packaging tests."""
    print("=" * 60)
    print("RUNNING PACKAGING TESTS")
    print("=" * 60)

    tests = [
        test_package_creation,
        test_package_structure,
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
