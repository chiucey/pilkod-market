#!/usr/bin/env python3
"""
Oil Price Analysis Skill Packager
Packs the skill into a distributable .skill bundle
"""

import os
import json
import shutil
from pathlib import Path

SKILL_DIR = Path("/workspace/temp-skills/marxist-oil-price-analysis")
OUTPUT_DIR = Path("/workspace/temp-skills")


def validate_skill():
    """Validate skill structure"""
    # Check SKILL.md exists and has frontmatter
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError("SKILL.md not found")

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            raise ValueError("SKILL.md must start with YAML frontmatter")
        if 'name:' not in content[:500]:
            raise ValueError("SKILL.md missing 'name' field")
        if 'description:' not in content[:500]:
            raise ValueError("SKILL.md missing 'description' field")

    # Check _meta.json exists and is valid
    meta_file = SKILL_DIR / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")

    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)
        if 'id' not in meta:
            raise ValueError("_meta.json missing 'id' field")
        if 'version' not in meta:
            raise ValueError("_meta.json missing 'version' field")

    print("✓ Skill structure validated")
    return True


def create_skill_bundle():
    """Create the .skill bundle"""
    skill_name = "marxist-oil-price-analysis"
    output_path = OUTPUT_DIR / f"{skill_name}.skill"

    # Remove existing if present
    if output_path.exists():
        output_path.unlink()

    # Create tar.gz archive
    import tarfile
    with tarfile.open(output_path, "w:gz") as tar:
        for root, dirs, files in os.walk(SKILL_DIR):
            # Skip empty directories
            if not files and not dirs:
                continue
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(SKILL_DIR)
                tar.add(file_path, arcname=arcname)

    print(f"✓ Skill bundle created: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    return output_path


def main():
    print("=" * 50)
    print("Oil Price Analysis Skill - Packager")
    print("=" * 50)

    validate_skill()
    bundle_path = create_skill_bundle()

    print("\n✓ Packager completed successfully!")
    print(f"Output: {bundle_path}")


if __name__ == "__main__":
    main()
