#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive from the skill directory.
"""

import os
import json
import zipfile
import sys
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """Package skill directory into a .skill file."""
    skill_path = skill_path.resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_path}")

    # Determine output location
    if output_dir is None:
        output_dir = skill_path.parent
    output_dir = output_dir.resolve()

    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_path.name}_{timestamp}.skill"

    # Read meta for version info
    meta_path = skill_path / "_meta.json"
    version = "1.0.0"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        version = meta.get("version", "1.0.0")

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # Skip __pycache__ and other temp files
                if '__pycache__' in str(file_path):
                    continue
                if file_path.name.endswith('.pyc'):
                    continue

                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"✅ Skill packaged successfully!")
    print(f"   Version: {version}")
    print(f"   Output: {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.2f} KB")

    return output_file


def main():
    # Get skill path from command line or use parent of scripts dir
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    output_file = package_skill(skill_path)
    print(f"\n📦 Skill archive ready: {output_file}")


if __name__ == "__main__":
    main()
