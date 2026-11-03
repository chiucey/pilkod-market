#!/usr/bin/env python3
"""
Package skill into a distributable .skill file
"""
import os
import json
import shutil
from pathlib import Path

def package_skill(skill_dir: str, output_dir: str = "."):
    skill_path = Path(skill_dir)
    output_path = Path(output_dir)

    # Validate skill structure
    skill_md = skill_path / "SKILL.md"
    meta_json = skill_path / "_meta.json"

    if not skill_md.exists():
        raise FileNotFoundError("SKILL.md not found")
    if not meta_json.exists():
        raise FileNotFoundError("_meta.json not found")

    # Read meta
    with open(meta_json, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', skill_path.name)
    version = meta.get('version', '1.0.0')

    # Create output name
    output_file = output_path / f"{skill_id}-{version}.skill"

    # Create zip archive
    shutil.make_archive(str(output_file.with_suffix('')), 'zip', skill_path)

    # Rename to .skill
    zip_file = output_file.with_suffix('.zip')
    if output_file.exists():
        output_file.unlink()
    shutil.move(str(zip_file), str(output_file))

    print(f"Skill packaged: {output_file}")
    return str(output_file)

if __name__ == "__main__":
    import sys
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    package_skill(skill_dir, output_dir)
