#!/usr/bin/env python3
"""
Package edu-ppt-creator skill for distribution.
Creates a .skill archive in the current directory.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def create_skill_archive(skill_dir: Path, output_dir: Path) -> Path:
    """Create a .skill archive from the skill directory."""
    skill_name = skill_dir.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Read version from _meta.json
    meta_path = skill_dir / "_meta.json"
    version = "1.0.0"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            version = meta.get("version", "1.0.0")
        except:
            pass

    output_name = f"{skill_name}_v{version}_{timestamp}.skill"
    output_path = output_dir / output_name

    # Create archive
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file() and '__pycache__' not in str(file_path):
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    return output_path


def validate_before_pack(skill_dir: Path) -> bool:
    """Quick validation before packaging."""
    required = ['SKILL.md', '_meta.json']
    for fname in required:
        if not (skill_dir / fname).exists():
            print(f"ERROR: Missing required file: {fname}")
            return False

    # Check frontmatter
    content = (skill_dir / 'SKILL.md').read_text(encoding='utf-8')
    if not content.startswith('---'):
        print("ERROR: SKILL.md must start with frontmatter")
        return False

    return True


def main():
    # Default to parent of scripts directory
    skill_dir = Path(__file__).parent.parent
    output_dir = Path.cwd()

    # Allow override via command line
    if len(sys.argv) > 1:
        skill_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])

    print(f"Packaging skill: {skill_dir}")
    print("-" * 50)

    if not skill_dir.exists():
        print(f"ERROR: Skill directory not found: {skill_dir}")
        return 1

    if not validate_before_pack(skill_dir):
        return 1

    try:
        output_path = create_skill_archive(skill_dir, output_dir)
        print(f"SUCCESS: Created {output_path.name}")
        print(f"  Path: {output_path}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
