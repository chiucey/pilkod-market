#!/usr/bin/env python3
"""
Test script for validation and packaging scripts.
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from quick_validate import validate_skill
from package_skill import package_skill, get_package_name


def test_validation_success():
    """Test validation with valid skill."""
    print("Testing validation with valid skill...")

    # Create a temporary valid skill structure
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()

        # Create valid SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill for validation.
---

# Test Skill

Some content here.
""", encoding="utf-8")

        # Create valid _meta.json
        meta_json = skill_dir / "_meta.json"
        meta_json.write_text('{"id": "12345", "version": "1.0.0"}', encoding="utf-8")

        # Validate
        success, errors = validate_skill(skill_dir)
        assert success, f"Expected success but got errors: {errors}"
        print("  ✅ Validation test passed")


def test_validation_missing_frontmatter():
    """Test validation with missing frontmatter name."""
    print("Testing validation with missing frontmatter...")

    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()

        # Create SKILL.md without proper frontmatter
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("# No Frontmatter\n\nContent.", encoding="utf-8")

        # Validate
        success, errors = validate_skill(skill_dir)
        assert not success, "Expected failure but got success"
        assert any("YAML frontmatter" in e for e in errors), f"Expected frontmatter error but got: {errors}"
        print("  ✅ Validation failure test passed")


def test_packaging():
    """Test packaging creates valid .skill file."""
    print("Testing packaging...")

    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()

        # Create valid SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill.
---

# Test
""", encoding="utf-8")

        # Create valid _meta.json
        meta_json = skill_dir / "_meta.json"
        meta_json.write_text('{"id": "12345", "version": "1.0.0"}', encoding="utf-8")

        # Create a reference file
        ref_dir = skill_dir / "references"
        ref_dir.mkdir()
        (ref_dir / "guide.md").write_text("# Guide\n\nSome guide content.", encoding="utf-8")

        # Package
        output_dir = Path(tmpdir) / "output"
        package_path = package_skill(skill_dir, output_dir)

        # Verify package exists
        assert Path(package_path).exists(), "Package file not created"

        # Verify it's a valid zip
        import zipfile
        with zipfile.ZipFile(package_path, 'r') as zf:
            names = zf.namelist()
            assert "SKILL.md" in names, "SKILL.md not in package"
            assert "_meta.json" in names, "_meta.json not in package"

        print(f"  ✅ Packaging test passed (package: {package_path})")


def main():
    print("=" * 50)
    print("Running validation and packaging tests...")
    print("=" * 50)

    try:
        test_validation_success()
        test_validation_missing_frontmatter()
        test_packaging()
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
