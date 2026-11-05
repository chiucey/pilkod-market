#!/usr/bin/env python3
"""
Patent Literature Reviewer Skill Packager
Generates distributable .skill files as .zip archives
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime


def get_skill_meta(skill_dir: str) -> dict:
    """Read skill metadata from _meta.json"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_skill_name(skill_dir: str) -> str:
    """Get skill name from directory name"""
    return os.path.basename(skill_dir)


def collect_files(skill_dir: str) -> list:
    """Collect files to be packaged"""
    files = []
    for root, dirs, filenames in os.walk(skill_dir):
        # Exclude hidden directories and temp files
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for filename in filenames:
            if filename.startswith('.') or filename.endswith('.pyc'):
                continue

            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, skill_dir)
            files.append(rel_path)

    return sorted(files)


def package_skill(skill_dir: str, output_dir: str = None) -> str:
    """
    Package skill as a .zip file

    Args:
        skill_dir: Path to skill directory
        output_dir: Output directory, defaults to parent of skill_dir

    Returns:
        Path to generated .zip file
    """
    if not os.path.isdir(skill_dir):
        raise ValueError(f"Not a directory: {skill_dir}")

    skill_name = get_skill_name(skill_dir)
    meta = get_skill_meta(skill_dir)
    version = meta.get('version', '1.0.0')

    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir) or '.'

    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = os.path.join(output_dir, f'{skill_name}_v{version}_{timestamp}.zip')

    # Collect files
    files = collect_files(skill_dir)

    if not files:
        raise ValueError("No files to package")

    # Create zip file
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            full_path = os.path.join(skill_dir, file)
            zf.write(full_path, file)

            # Security check: prevent symlink escape
            real_path = os.path.realpath(full_path)
            skill_real_path = os.path.realpath(skill_dir)
            if not real_path.startswith(skill_real_path):
                raise ValueError(f"Security check failed: {file} is outside skill directory")

    print(f"Skill packaged successfully: {output_file}")
    print(f"Files included: {len(files)}")
    for f in files:
        print(f"  - {f}")

    return output_file


def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    print("=" * 50)
    print("Patent Literature Reviewer Skill Packager")
    print("=" * 50)

    try:
        output_file = package_skill(skill_dir)
        print("=" * 50)
        print(f"Package created: {output_file}")
    except Exception as e:
        print("=" * 50)
        print(f"Packaging failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
