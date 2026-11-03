#!/usr/bin/env python3
"""
Package the design-system-inspiration skill into a distributable .skill file.
"""

import os
import json
import shutil
import zipfile
from pathlib import Path

SKILL_DIR = Path("/workspace/temp-skills/design-system-inspiration")
OUTPUT_DIR = Path("/workspace/temp-skills/packages")
SKILL_NAME = "design-system-inspiration"
OUTPUT_FILE = OUTPUT_DIR / f"{SKILL_NAME}.skill"

def validate_skill():
    """Validate skill structure before packaging."""
    # Check SKILL.md exists and has frontmatter
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError("SKILL.md not found")

    with open(skill_md, 'r') as f:
        content = f.read()
        if not content.startswith('---'):
            raise ValueError("SKILL.md must start with frontmatter (---)")
        if 'name:' not in content or 'description:' not in content:
            raise ValueError("SKILL.md must have name and description in frontmatter")

    # Check _meta.json
    meta = SKILL_DIR / "_meta.json"
    if not meta.exists():
        raise FileNotFoundError("_meta.json not found")

    with open(meta, 'r') as f:
        meta_data = json.load(f)
        if 'id' not in meta_data or 'version' not in meta_data:
            raise ValueError("_meta.json must have 'id' and 'version' fields")

    print("✅ Validation passed")
    return True

def package_skill():
    """Package the skill into a .skill file."""
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Remove existing output
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    # Create zip file
    with zipfile.ZipFile(OUTPUT_FILE, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            # Skip hidden files and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(SKILL_DIR)
                zf.write(file_path, arcname)

    print(f"✅ Skill packaged: {OUTPUT_FILE}")
    print(f"   Size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    return str(OUTPUT_FILE)

if __name__ == "__main__":
    print(f"Packaging {SKILL_NAME}...")
    validate_skill()
    output_path = package_skill()
    print(f"\n📦 Package ready: {output_path}")
