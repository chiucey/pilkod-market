#!/usr/bin/env python3
"""
Package skill into distributable .skill file
Creates a zip archive of the skill directory
"""

import os
import sys
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

def get_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package skill into .skill file"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # Determine output directory
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_path.parent / "dist"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # Files to include (no build artifacts or secrets)
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.DS_Store',
        '*.pyc',
        '*.pyo',
        '.env',
        'node_modules',
        'dist',
        '.venv',
        'venv'
    ]

    # Create zip file
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # Check if file should be excluded
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern.startswith('*'):
                        if file_path.suffix == pattern[1:]:
                            should_exclude = True
                            break
                    elif pattern in str(file_path):
                        should_exclude = True
                        break

                if should_exclude:
                    continue

                # Add file to zip with relative path
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✅ Skill packaged: {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")

    return str(output_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = sys.argv[1]

    output_file = package_skill(skill_path)
    print(f"\nOutput: {output_file}")
