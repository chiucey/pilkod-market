#!/usr/bin/env python3
"""
Package skill into a distributable .skill file
Creates a clean archive with only necessary files
"""

import os
import zipfile
import json
import sys
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package skill into .skill file"""
    skill_dir = Path(skill_path)

    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_path}")

    # Determine output path
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_dir.parent

    skill_name = skill_dir.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"{skill_name}_{timestamp}.skill"

    # Files to include (whitelist approach)
    allowed_files = {
        'SKILL.md',
        '_meta.json',
    }
    allowed_dirs = {'scripts', 'references', 'assets'}

    # Create archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add main files
        for file in allowed_files:
            file_path = skill_dir / file
            if file_path.exists():
                zf.write(file_path, file)
                print(f"  + {file}")

        # Add directories
        for dir_name in allowed_dirs:
            dir_path = skill_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        # Skip test files and __pycache__
                        if '__pycache__' in root or file.endswith('_test.py'):
                            continue
                        file_abs = Path(root) / file
                        file_rel = file_abs.relative_to(skill_dir)
                        zf.write(file_abs, file_rel)
                        print(f"  + {file_rel}")

    print(f"\n✅ Skill packaged: {output_file}")
    return str(output_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/video-script-writer"
    else:
        skill_path = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    package_skill(skill_path, output_dir)