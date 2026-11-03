#!/usr/bin/env python3
"""Skill packaging script for cognitive-lens"""

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

def validate_skill(skill_path: Path) -> bool:
    """Validate skill structure"""
    errors = []

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
    else:
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append("SKILL.md must start with frontmatter (---)")
        if "name:" not in content:
            errors.append("SKILL.md missing 'name:' in frontmatter")
        if "description:" not in content:
            errors.append("SKILL.md missing 'description:' in frontmatter")

    # Check _meta.json exists
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json missing 'id'")
            if "version" not in meta:
                errors.append("_meta.json missing 'version'")
        except json.JSONDecodeError:
            errors.append("_meta.json is invalid JSON")

    if errors:
        print("❌ Validation failed:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("✅ Validation passed")
    return True

def package_skill(skill_path: Path, output_dir: Path) -> Path:
    """Package skill into .skill file"""
    skill_name = skill_path.name
    output_file = output_dir / f"{skill_name}.skill"

    # Create zip
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  ✓ {arcname}")

    return output_file

def main():
    if len(sys.argv) < 2:
        skill_path = Path("/workspace/temp-skills/cognitive-lens")
    else:
        skill_path = Path(sys.argv[1])

    print(f"\n📦 Packaging skill: {skill_path}")
    print("=" * 50)

    # Validate
    if not validate_skill(skill_path):
        sys.exit(1)

    # Package
    print("\n📁 Creating package...")
    output_dir = skill_path.parent
    output_file = package_skill(skill_path, output_dir)

    print(f"\n✅ Skill packaged successfully!")
    print(f"   Output: {output_file}")
    print(f"   Size: {output_file.stat().st_size:,} bytes")

if __name__ == "__main__":
    main()
