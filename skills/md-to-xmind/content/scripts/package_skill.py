#!/usr/bin/env python3
"""
Package script for md-to-xmind skill.
Creates a distributable .skill package.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path


def package_skill(skill_dir: str, output_dir: str = './dist') -> str:
    """Package the skill into a .skill file."""
    skill_path = Path(skill_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    package_name = f"{skill_path.name}.skill"
    package_path = output_path / package_name

    # Files to include
    include_patterns = ['SKILL.md', '_meta.json', 'scripts/', 'references/', 'assets/']
    exclude_patterns = ['__pycache__', '.pyc', '.git', '.DS_Store', '*.log', 'test_*.py']

    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Filter directories
            dirs[:] = [d for d in dirs if not any(
                pattern.rstrip('/') == d for pattern in exclude_patterns
            )]

            for file in files:
                # Skip excluded files
                if any(file.endswith(pattern.lstrip('*'))
                       for pattern in exclude_patterns if '*' in pattern):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"Packaged skill to: {package_path}")
    return str(package_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        skill_dir = '../md-to-xmind'
    else:
        skill_dir = sys.argv[1]

    result = package_skill(skill_dir)
    print(f"Done: {result}")
