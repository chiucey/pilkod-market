#!/usr/bin/env python3
"""
Package skill for distribution
Creates a .skill file containing the skill bundle
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def get_safe_filename(name: str) -> str:
    """Convert skill name to safe filename"""
    return name.replace('-', '_')

def package_skill(skill_dir: Path, output_dir: Path = None):
    """Package a skill into a distributable .skill file"""

    skill_dir = skill_dir.resolve()
    name = skill_dir.name

    # Read meta.json to get version
    meta_path = skill_dir / '_meta.json'
    if not meta_path.exists():
        raise FileNotFoundError("_meta.json not found")

    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    version = meta['version']
    skill_id = meta['id']

    # Output setup
    if output_dir is None:
        output_dir = Path('/workspace/temp-skills')

    safe_name = get_safe_filename(name)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"{safe_name}_{version}.skill"

    # Files to include (no secrets, no temp files)
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '.DS_Store',
        '*.log',
        '.git',
        '.venv',
        'venv',
        'node_modules'
    ]

    print(f"Packaging skill: {name}")
    print(f"Version: {version}")
    print(f"ID: {skill_id}")
    print(f"Output: {output_file}")

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', '.venv', 'venv']]

            for file in files:
                # Skip excluded files
                if any(file.endswith(pat.replace('*', '')) for pat in exclude_patterns):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)

                # Security check: no symlinks or absolute paths
                if os.path.islink(file_path):
                    print(f"Warning: Skipping symlink {arcname}")
                    continue

                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    # Get archive size
    size_kb = output_file.stat().st_size / 1024
    print(f"\n✓ Packaged successfully: {output_file}")
    print(f"  Size: {size_kb:.1f} KB")

    # Verify the package
    print("\nVerifying package contents...")
    with zipfile.ZipFile(output_file, 'r') as zf:
        file_list = zf.namelist()
        required_files = ['SKILL.md', '_meta.json']
        for req in required_files:
            if req not in file_list:
                raise ValueError(f"Required file {req} missing from package")
        print(f"  ✓ Contains {len(file_list)} files")
        print(f"  ✓ All required files present")

    return output_file

def main():
    skill_dir = Path('/workspace/temp-skills/url-image-crawler')

    if not skill_dir.exists():
        print(f"Error: Skill directory not found: {skill_dir}")
        return 1

    try:
        output_file = package_skill(skill_dir)
        print(f"\n{'=' * 50}")
        print(f"Package ready: {output_file}")
        print(f"{'=' * 50}")
        return 0
    except Exception as e:
        print(f"\n✗ Packaging failed: {e}")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
