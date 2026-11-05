#!/usr/bin/env python3
"""
Package Skill Script
Packages the doodle-tutor skill into a .skill file
"""

import json
import os
import shutil
import tarfile
from pathlib import Path

SKILL_DIR = Path("/workspace/temp-skills/doodle-tutor")
OUTPUT_DIR = Path("/workspace/temp-skills/packages")
OUTPUT_FILE = OUTPUT_DIR / "doodle-tutor-1.0.0.skill"


def validate_skill():
    """Validate skill structure"""
    errors = []

    # Check SKILL.md exists and has valid frontmatter
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
    else:
        content = skill_md.read_text()
        if not content.startswith("---"):
            errors.append("SKILL.md must start with frontmatter (---)")
        if "name:" not in content or "description:" not in content:
            errors.append("SKILL.md missing required frontmatter fields")

    # Check _meta.json exists and is valid
    meta_json = SKILL_DIR / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            meta = json.loads(meta_json.read_text())
            if "id" not in meta:
                errors.append("_meta.json missing 'id' field")
            if "version" not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError:
            errors.append("_meta.json is not valid JSON")

    return errors


def package_skill():
    """Package the skill into a .skill file"""
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Remove existing output file if present
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    # Create tar.gz archive
    with tarfile.open(OUTPUT_FILE, "w:gz") as tar:
        # Add all files from skill directory
        for root, dirs, files in os.walk(SKILL_DIR):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(SKILL_DIR)
                tar.add(file_path, arcname=arcname)

    print(f"✅ Skill packaged successfully: {OUTPUT_FILE}")
    print(f"   Size: {OUTPUT_FILE.stat().st_size} bytes")
    return OUTPUT_FILE


def main():
    print("=" * 50)
    print("Packaging doodle-tutor skill...")
    print("=" * 50)

    # Validate
    print("\n🔍 Validating skill structure...")
    errors = validate_skill()
    if errors:
        print("\n❌ Validation failed:")
        for error in errors:
            print(f"   - {error}")
        return False

    print("✅ Validation passed!")

    # Package
    print("\n📦 Packaging skill...")
    output_file = package_skill()

    print("\n" + "=" * 50)
    print("✅ Packaging complete!")
    print("=" * 50)

    return True


if __name__ == "__main__":
    main()
